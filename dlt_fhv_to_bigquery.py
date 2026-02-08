import os
import sys
import tempfile
import requests
import pandas as pd
import dlt
from dotenv import load_dotenv

# -----------------------------
# 1) Load env vars from .env
# -----------------------------
load_dotenv()

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
BQ_DATASET = os.getenv("BQ_DATASET")

if not PROJECT_ID or not BQ_DATASET:
    raise ValueError("Missing GCP_PROJECT_ID or BQ_DATASET in .env")

# -----------------------------
# 2) Data source (DataTalksClub backup)
# -----------------------------
BASE_URL = "https://github.com/DataTalksClub/nyc-tlc-data/releases/download/fhv"
MONTHS = ["2019-01", "2019-02", "2019-03"]  # extend later if needed

def download_to_tempfile(url: str) -> str:
    """Stream download to a temp file to avoid keeping the whole file in RAM."""
    r = requests.get(url, stream=True, timeout=120)
    r.raise_for_status()

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv.gz")
    with open(tmp.name, "wb") as f:
        for chunk in r.iter_content(chunk_size=1024 * 1024):  # 1MB chunks
            if chunk:
                f.write(chunk)
    return tmp.name

def fhv_tripdata_resource(chunksize: int):
    @dlt.resource(
        name="fhv_tripdata_dlt",          # ✅ NEW TABLE NAME
        write_disposition="append"        # append to the DLT table
    )
    def fhv_tripdata_dlt():
        for m in MONTHS:
            url = f"{BASE_URL}/fhv_tripdata_{m}.csv.gz"
            gz_path = download_to_tempfile(url)

            for df_chunk in pd.read_csv(gz_path, compression="gzip", chunksize=chunksize):
                df_chunk.columns = [c.strip() for c in df_chunk.columns]
                df_chunk["source_month"] = m
                yield df_chunk.to_dict(orient="records")

    return fhv_tripdata_dlt

def main():
    # allow: python dlt_fhv_to_bigquery.py 200000
    chunksize = 200_000
    if len(sys.argv) > 1:
        chunksize = int(sys.argv[1])

    print(f"Using CHUNKSIZE={chunksize}")
    print(f"Target: {PROJECT_ID}.{BQ_DATASET}.fhv_tripdata_dlt")

    pipeline = dlt.pipeline(
        pipeline_name="nyc_fhv_pipeline",
        destination="bigquery",
        dataset_name=BQ_DATASET
    )

    info = pipeline.run(fhv_tripdata_resource(chunksize)())
    print(info)
    print(f"Loaded into: {PROJECT_ID}.{BQ_DATASET}.fhv_tripdata_dlt")

if __name__ == "__main__":
    main()
