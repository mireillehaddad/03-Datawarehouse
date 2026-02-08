import os
import requests
import pandas as pd
import dlt

from io import BytesIO
from dotenv import load_dotenv

# ------------------------------------------------------------
# 1) Load environment variables from .env
# ------------------------------------------------------------
load_dotenv()

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
BQ_DATASET = os.getenv("BQ_DATASET")

if not PROJECT_ID or not BQ_DATASET:
    raise ValueError("Missing GCP_PROJECT_ID or BQ_DATASET in .env")

# ------------------------------------------------------------
# 2) Define data source (DataTalksClub backup release)
#    We'll start with 2019-01 to 2019-03 like your manual steps.
# ------------------------------------------------------------
BASE_URL = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/fhv"

MONTHS = ["2019-01", "2019-02", "2019-03"]  # extend later if you want

def fetch_fhv_csv_gz(month: str) -> pd.DataFrame:
    """
    Downloads one FHV month .csv.gz into memory and returns a DataFrame.
    """
    url = f"{BASE_URL}/fhv_tripdata_{month}.csv.gz"
    r = requests.get(url, timeout=120)
    r.raise_for_status()

    # pandas can read gzip directly from bytes
    df = pd.read_csv(BytesIO(r.content), compression="gzip")

    # Optional: standardize column names (DLT handles this, but nice for consistency)
    df.columns = [c.strip() for c in df.columns]
    df["source_month"] = month  # helpful lineage column

    return df

@dlt.resource(name="fhv_tripdata", write_disposition="merge", primary_key=None)
def fhv_tripdata():
    """
    DLT resource that yields records month by month.
    """
    for m in MONTHS:
        df = fetch_fhv_csv_gz(m)
        # yield rows as dicts
        yield df.to_dict(orient="records")

# ------------------------------------------------------------
# 3) Run pipeline into BigQuery
# ------------------------------------------------------------
pipeline = dlt.pipeline(
    pipeline_name="nyc_fhv_pipeline",
    destination="bigquery",
    dataset_name=BQ_DATASET
)

load_info = pipeline.run(fhv_tripdata())
print(load_info)
print(f"Loaded into: {PROJECT_ID}.{BQ_DATASET}.fhv_tripdata")
