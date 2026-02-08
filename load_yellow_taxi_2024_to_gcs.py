import os
import urllib.request
import time
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv
from google.cloud import storage

# ==================================
# 1) Load environment variables
# ==================================

load_dotenv()

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
GCS_BUCKET = os.getenv("GCS_BUCKET")

if not PROJECT_ID or not GCS_BUCKET:
    raise ValueError("Missing GCP_PROJECT_ID or GCS_BUCKET in .env")

# ==================================
# 2) Configuration
# ==================================

BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"
MONTHS = [f"{i:02d}" for i in range(1, 7)]  # January to June 2024

DOWNLOAD_DIR = "data/yellow_2024"
CHUNK_SIZE = 8 * 1024 * 1024  # 8 MB
MAX_WORKERS = 4

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Use Application Default Credentials
storage_client = storage.Client(project=PROJECT_ID)
bucket = storage_client.bucket(GCS_BUCKET)

# ==================================
# 3) Helper functions
# ==================================

def download_file(month: str) -> str | None:
    filename = f"yellow_tripdata_2024-{month}.parquet"
    url = f"{BASE_URL}/{filename}"
    local_path = os.path.join(DOWNLOAD_DIR, filename)

    try:
        print(f"Downloading {filename}")
        urllib.request.urlretrieve(url, local_path)
        return local_path
    except Exception as e:
        print(f"Failed to download {filename}: {e}")
        return None


def upload_to_gcs(file_path: str, retries: int = 3):
    blob_name = os.path.basename(file_path)
    blob = bucket.blob(blob_name)
    blob.chunk_size = CHUNK_SIZE

    for attempt in range(1, retries + 1):
        try:
            print(f"Uploading {blob_name} to gs://{GCS_BUCKET}/")
            blob.upload_from_filename(file_path)

            if blob.exists(storage_client):
                print(f"Upload verified: {blob_name}")
                return
        except Exception as e:
            print(f"Attempt {attempt} failed for {blob_name}: {e}")
            time.sleep(5)

    print(f"Giving up on {blob_name}")


# ==================================
# 4) Main
# ==================================

def main():
    print("Starting Yellow Taxi 2024 upload to GCS")
    print(f"Project: {PROJECT_ID}")
    print(f"Bucket: {GCS_BUCKET}")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        downloaded_files = list(executor.map(download_file, MONTHS))

    valid_files = [f for f in downloaded_files if f is not None]

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(upload_to_gcs, valid_files)

    print("All files processed.")


if __name__ == "__main__":
    main()
