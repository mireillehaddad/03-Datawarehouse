✅ 1) Download FHV files from the DataTalksClub backup (works even when TLC/CloudFront blocks)
```bash
mkdir -p data/fhv
cd data/fhv


wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/fhv/fhv_tripdata_2019-01.csv.gz
wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/fhv/fhv_tripdata_2019-02.csv.gz
wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/fhv/fhv_tripdata_2019-03.csv.gz
```

✅ 2) Option A (simple): unzip to CSV, then upload to your bucket

Unzip:

```bash
gunzip -k fhv_tripdata_2019-01.csv.gz
gunzip -k fhv_tripdata_2019-02.csv.gz
gunzip -k fhv_tripdata_2019-03.csv.gz
```

Upload to your bucket under a prefix fhv/ (no need to “mkdir” in GCS):

```bash
gsutil -m cp fhv_tripdata_2019-0*.csv gs://calm-snowfall-485503-b4-terra-bucket/fhv/

```



Verify:

```bash
gsutil ls gs://calm-snowfall-485503-b4-terra-bucket/fhv/ | head


```

✅ 3) Create the external table in Bigquery:
```bash
CREATE OR REPLACE EXTERNAL TABLE `calm-snowfall-485503-b4.demo_dataset_ny_taxi.fhv_tripdata`
OPTIONS (
  format = 'CSV',
  uris = ['gs://calm-snowfall-485503-b4-terra-bucket/fhv/fhv_tripdata_2019-*.csv'],
  skip_leading_rows = 1
);


```

Quick check:
```bash
SELECT COUNT(*) FROM `calm-snowfall-485503-b4.demo_dataset_ny_taxi.fhv_tripdata`;


```




# FHV Tripdata (2019 Q1) — What I did in my environment

Project: `calm-snowfall-485503-b4`  
Dataset: `demo_dataset_ny_taxi`  
Bucket: `calm-snowfall-485503-b4-terra-bucket`  
Workspace: `/workspaces/03-Datawarehouse`

---

## 1) I checked what was already in my GCS bucket

I first listed the bucket contents to confirm what data I already had uploaded.

```bash
gsutil ls gs://calm-snowfall-485503-b4-terra-bucket/
```

At that point, I could see my `yellow_tripdata_...` and `green_tripdata_...` files and the `taxi_ml_model/` folder, but **no FHV files**.

---

## 2) I tried to “create a folder” in GCS (and learned I don’t need to)

I attempted this:

```bash
gsutil mkdir gs://calm-snowfall-485503-b4-terra-bucket/fhv/
```

It failed because:
- `gsutil mkdir` is not a valid command.
- In GCS, “folders” are just **prefixes**. The `fhv/` prefix appears automatically when I upload objects into `.../fhv/...`.

---

## 3) I tried uploading FHV files before downloading them (and it failed)

I tried to upload files like this:

```bash
gsutil -m cp fhv_tripdata_2019-*.csv gs://calm-snowfall-485503-b4-terra-bucket/fhv/
```

It failed because I didn’t have any `fhv_tripdata_2019-*.csv` files locally yet, so the wildcard matched nothing.

---

## 4) I created a local folder for the FHV downloads

```bash
mkdir -p data/fhv
cd data/fhv
```

---

## 5) I tried downloading from TLC CloudFront (403 Forbidden)

I initially tried the TLC CloudFront links:

```bash
wget https://d37ci6vzurychx.cloudfront.net/trip-data/fhv_tripdata_2019-01.csv
wget https://d37ci6vzurychx.cloudfront.net/trip-data/fhv_tripdata_2019-02.csv
wget https://d37ci6vzurychx.cloudfront.net/trip-data/fhv_tripdata_2019-03.csv
```

All three returned **403 Forbidden**, so I switched to the DataTalksClub backup.

---

## 6) I downloaded the FHV files from the DataTalksClub GitHub backup (success)

```bash
wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/fhv/fhv_tripdata_2019-01.csv.gz
wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/fhv/fhv_tripdata_2019-02.csv.gz
wget https://github.com/DataTalksClub/nyc-tlc-data/releases/download/fhv/fhv_tripdata_2019-03.csv.gz
```

I verified they were downloaded:

```bash
ls -lh
```

---

## 7) I unzipped the files to CSV (and kept the `.gz` copies)

```bash
gunzip -k fhv_tripdata_2019-01.csv.gz
gunzip -k fhv_tripdata_2019-02.csv.gz
gunzip -k fhv_tripdata_2019-03.csv.gz
```

---

## 8) I uploaded the CSV files to GCS under the `fhv/` prefix (success)

I uploaded the 3 CSVs into `gs://calm-snowfall-485503-b4-terra-bucket/fhv/`:

```bash
gsutil -m cp fhv_tripdata_2019-0*.csv gs://calm-snowfall-485503-b4-terra-bucket/fhv/
```

Then I verified the objects exist:

```bash
gsutil ls gs://calm-snowfall-485503-b4-terra-bucket/fhv/ | head
```

Expected output (3 files):

- `gs://calm-snowfall-485503-b4-terra-bucket/fhv/fhv_tripdata_2019-01.csv`
- `gs://calm-snowfall-485503-b4-terra-bucket/fhv/fhv_tripdata_2019-02.csv`
- `gs://calm-snowfall-485503-b4-terra-bucket/fhv/fhv_tripdata_2019-03.csv`

---

## 9) I went back to my repo root

```bash
cd /workspaces/03-Datawarehouse/
ls
```

---

## 10) I created a `.env` file for my project/dataset/bucket (and ignored it in git)

```bash
cat > .env << 'EOF'
GCP_PROJECT_ID=calm-snowfall-485503-b4
BQ_DATASET=demo_dataset_ny_taxi
GCS_BUCKET=calm-snowfall-485503-b4-terra-bucket
EOF
```

```bash
echo ".env" >> .gitignore
```

---

## 11) I authenticated with Google Cloud (CLI + ADC for Python)

User login (for CLI tools like `bq`/`gsutil`):

```bash
gcloud auth login
gcloud config set project calm-snowfall-485503-b4
```

Application Default Credentials (needed for Python libraries like BigQuery client + DLT):

```bash
gcloud auth application-default login
```

---

## 12) I installed Python dependencies (DLT + BigQuery support)

```bash
pip install -U dlt python-dotenv pandas requests pyarrow
pip install -U "dlt[bigquery]"
pip install -U google-cloud-bigquery-storage
```

---

## 13) What happened when I tried the DLT approach

I tried running a DLT ingestion script to load FHV into BigQuery, but I ran into multiple issues:

1) **DLT API mismatch**
- I got an error like:
  - `TypeError: pipeline got an unexpected keyword argument destination_kwargs`
- This happened because the script used an argument that my installed DLT version did not support.

2) **It was slow/heavy and I interrupted it several times**
- I tried different chunk sizes (`200000`, `100000`, `50000`) and pressed `CTRL+C` multiple times.

3) **A real normalization failure**
- Eventually, I hit:
  - `Type is not JSON serializable: DateTime`
- DLT failed during the **normalize** step because a datetime-like object couldn’t be encoded into JSON the way the pipeline expected.

DLT also mentioned it left **pending packages**, which can block new loads until I either retry or drop them.

---

## 14) Why my manual GCS → External Table → BigQuery SQL approach is better here

For this homework-style ingestion, I already have flat files in GCS, so BigQuery can read them directly. That means I can avoid:
- long-running Python jobs,
- local temp files,
- serialization issues,
- DLT pipeline state (pending packages).

So for this case, the simplest and most reliable approach is:

1) Upload CSVs to GCS  
2) Create an **EXTERNAL table** in BigQuery pointing to those CSVs  
3) Optionally materialize into a native BigQuery table with **CTAS** (`CREATE TABLE AS SELECT`)  

---

## 15) When I would use DLT vs when I would not

### I use DLT when:
- I’m ingesting from APIs (pagination/auth/retries)
- I need incremental loads / stateful ingestion
- I want schema evolution handled automatically
- I want a repeatable, production-style pipeline I can schedule

### I do NOT use DLT when:
- The source is already **files in GCS**
- BigQuery can query the files directly (external table) and I only need analytics
- I need a quick/simple homework setup with minimal moving parts

In my FHV case (CSV files already in my bucket), BigQuery SQL is the cleanest solution.

