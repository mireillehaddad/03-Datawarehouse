
# Module 3 – Data Warehousing & BigQuery
## Loading Yellow Taxi Data (January–June 2024)

**Project:** `calm-snowfall-485503-b4`  
**Dataset:** `demo_dataset_ny_taxi`  
**GCS Bucket:** `calm-snowfall-485503-b4-terra-bucket`  

---

## 1. Environment setup

I configured my environment variables using a `.env` file to avoid hardcoding project-specific values.

```bash
GCP_PROJECT_ID=calm-snowfall-485503-b4
BQ_DATASET=demo_dataset_ny_taxi
GCS_BUCKET=calm-snowfall-485503-b4-terra-bucket
```

The `.env` file is excluded from version control via `.gitignore`.

---

## 2. Authentication

I authenticated using Google Cloud CLI and Application Default Credentials so that both CLI tools and Python libraries could access Google Cloud services.

```bash
gcloud auth login
gcloud config set project calm-snowfall-485503-b4
gcloud auth application-default login
```

---

## 3. Downloading Yellow Taxi Parquet files (Jan–Jun 2024)

I downloaded the Yellow Taxi Trip Records in **Parquet format** for January through June 2024 from the official NYC TLC CloudFront endpoint.

The files downloaded are:

- `yellow_tripdata_2024-01.parquet`
- `yellow_tripdata_2024-02.parquet`
- `yellow_tripdata_2024-03.parquet`
- `yellow_tripdata_2024-04.parquet`
- `yellow_tripdata_2024-05.parquet`
- `yellow_tripdata_2024-06.parquet`

The download and upload process is automated using a Python script.

---

## 4. Uploading data to Google Cloud Storage

I used a Python script (`load_yellow_taxi_2024_to_gcs.py`) that performs the following steps:

1. Loads project and bucket information from the `.env` file  
2. Downloads each monthly Parquet file locally  
3. Uploads the files to my GCS bucket  
4. Verifies that each file exists in GCS after upload  
5. Uses parallel execution to speed up the process  

To run the script:

```bash
python load_yellow_taxi_2024_to_gcs.py
```

---

## 5. Verifying uploaded files in GCS

After the script completed, I verified that all Parquet files were successfully uploaded to my bucket.

```bash
gsutil ls gs://calm-snowfall-485503-b4-terra-bucket/yellow_tripdata_2024-*.parquet
```

This confirmed that all six monthly files are available in Google Cloud Storage.

---





BigQuery Setup Create an external table using the Yellow Taxi Trip Records.
 Create a (regular/materialized) table in BQ using the Yellow Taxi Trip Records (do not partition or cluster this table).

 ### 1) Create the external table (reads Parquet directly from GCS)
 This table does not store data in BigQuery. It queries the Parquet files “in place” in my bucket.
 
```bash
CREATE OR REPLACE EXTERNAL TABLE `calm-snowfall-485503-b4.demo_dataset_ny_taxi.yellow_tripdata_2024_ext`
OPTIONS (
  format = 'PARQUET',
  uris = ['gs://calm-snowfall-485503-b4-terra-bucket/yellow_tripdata_2024-*.parquet']
);
```


Quick check:
 
```bash
SELECT COUNT(*) AS row_count
FROM `calm-snowfall-485503-b4.demo_dataset_ny_taxi.yellow_tripdata_2024_ext`;

```

### 2) Create a regular BigQuery table (NOT partitioned, NOT clustered)

This table copies the data into BigQuery storage (faster queries, but uses BQ storage).

```bash
CREATE OR REPLACE TABLE `calm-snowfall-485503-b4.demo_dataset_ny_taxi.yellow_tripdata_2024`
AS
SELECT *
FROM `calm-snowfall-485503-b4.demo_dataset_ny_taxi.yellow_tripdata_2024_ext`;
```

Quick check (should match the external table count):

```bash
SELECT COUNT(*) AS count_rows
FROM `calm-snowfall-485503-b4.demo_dataset_ny_taxi.yellow_tripdata_2024`;
```



# Homework 3 Solution:

### Question 1. Counting records

**What is the count of records for the 2024 Yellow Taxi Data (January–June 2024)?**

**Answer:** ✅ **20,332,093**

**Explanation:**

The total number of records was computed using the external table created on top of the Parquet files stored in Google Cloud Storage:

```sql
SELECT COUNT(*)
FROM `calm-snowfall-485503-b4.demo_dataset_ny_taxi.yellow_tripdata_2024_ext`;

### Question 2. Data read estimation

**Task:**  
Write a query to count the distinct number of `PULocationID` values for the entire dataset on both:
- the **External Table**
- the **Materialized (regular) Table**

Example query used on both tables:

```sql
SELECT COUNT(DISTINCT PULocationID)
FROM `calm-snowfall-485503-b4.demo_dataset_ny_taxi.yellow_tripdata_2024_ext`;

```
**Answer:** ✅ **18.82 MB for the External Table and 47.60 MB for the Materialized Table**

Explanation:

The External Table reads data directly from Parquet files in Google Cloud Storage.
Because Parquet is a columnar format, BigQuery only scans the required column (PULocationID), resulting in a relatively small amount of data read.

The Materialized (regular) Table stores data internally in BigQuery’s storage format.
Even though it is optimized, scanning a distinct column across the full table still requires reading more data than the external Parquet-backed table in this case.


### Question 3. Understanding columnar storage

**Task:**  
Write two queries on the **materialized (regular) BigQuery table**:

1. Retrieve only `PULocationID`
```sql
SELECT PULocationID
FROM `calm-snowfall-485503-b4.demo_dataset_ny_taxi.yellow_tripdata_2024`;

```
**Answer:** ✅ **BigQuery is a columnar database, and it only scans the specific columns requested in the query. Querying two columns (PULocationID, DOLocationID) requires reading more data than querying one column (PULocationID), leading to a higher estimated number of bytes processed.**

Explanation:

BigQuery stores data in a columnar format, meaning each column is stored separately.

When a query selects only one column, BigQuery reads data only for that column.

When a query selects multiple columns, BigQuery must read data for each selected column.

As a result, selecting more columns increases the amount of data scanned and therefore the estimated bytes processed.

The other options are incorrect because:

BigQuery does not duplicate data across partitions for column selection.

Caching does not affect the estimated bytes scanned.

Selecting multiple columns does not trigger implicit joins.

### Question 4. Counting zero fare trips

**Task:**  
Count how many records in the **2024 Yellow Taxi dataset** have a `fare_amount` equal to `0`.

**Query:**
```sql
SELECT COUNT(*) AS zero_fare_trips
FROM `calm-snowfall-485503-b4.demo_dataset_ny_taxi.yellow_tripdata_2024`
WHERE fare_amount = 0;

```

**Answer:** ** ✅ 8,333** 

Explanation:

This query filters the Yellow Taxi trips dataset for records where fare_amount is exactly zero and counts the number of such trips.
The result reflects the data loaded for January–June 2024 only, based on the parquet files present in the GCS bucket.

### Question 5. Partitioning and clustering

**Question:**  
What is the best strategy to optimize a BigQuery table if queries always:
- filter on `tpep_dropoff_datetime`
- order results by `VendorID`

**Correct answer:**  
✅ **Partition by `tpep_dropoff_datetime` and cluster on `VendorID`**

**Explanation:**  

- **Partitioning** on `tpep_dropoff_datetime` reduces the amount of data scanned by limiting queries to relevant date partitions.
- **Clustering** on `VendorID` improves performance for queries that sort or filter by this column within each partition.
- BigQuery supports **one partitioning column** and **multiple clustering columns**, making this combination optimal for the given query pattern.

**Table creation example:**
```sql
CREATE TABLE `calm-snowfall-485503-b4.demo_dataset_ny_taxi.yellow_tripdata_2024_partitioned_clustered`
PARTITION BY DATE(tpep_dropoff_datetime)
CLUSTER BY VendorID AS
SELECT *
FROM `calm-snowfall-485503-b4.demo_dataset_ny_taxi.yellow_tripdata_2024`;

```

verification:
```sql
SELECT
  table_name,
  column_name,
  is_partitioning_column,
  clustering_ordinal_position
FROM `calm-snowfall-485503-b4.demo_dataset_ny_taxi.INFORMATION_SCHEMA.COLUMNS`
WHERE table_name = 'yellow_tripdata_2024_partitioned_clustered'
  AND (is_partitioning_column = 'YES'
       OR clustering_ordinal_position IS NOT NULL)
ORDER BY clustering_ordinal_position;

```

![
](image.png)


### Question 6. Partition benefits

To compare the effect of partitioning, I ran the same query on:
1) the non-partitioned table (`yellow_tripdata_2024`)
2) the partitioned+clustered table (`yellow_tripdata_2024_partitioned_clustered`)

A) Run on the non-partitioned (materialized) table

```sql

SELECT DISTINCT VendorID
FROM `calm-snowfall-485503-b4.demo_dataset_ny_taxi.yellow_tripdata_2024`
WHERE DATE(tpep_dropoff_datetime) BETWEEN '2024-03-01' AND '2024-03-15';
```
B) Run on the partitioned + clustered table (from Q5)

```sql
SELECT DISTINCT VendorID
FROM `calm-snowfall-485503-b4.demo_dataset_ny_taxi.yellow_tripdata_2024_partitioned_clustered`
WHERE DATE(tpep_dropoff_datetime) BETWEEN '2024-03-01' AND '2024-03-15';
```
What to observe

In the BigQuery UI, after you paste each query, look at:

This query will process … (bytes processed / estimated bytes)

**Correct answer 6:** 
✅ 310.24 MB for non-partitioned table and 26.84 MB for the partitioned table

### Question 7. External table storage

**Question:**  
Where is the data stored in the External Table you created?

**Correct answer:**  
✅ **GCP Bucket**

**Explanation:**  
An **external table** in BigQuery does not store the data inside BigQuery itself.  
Only the table metadata is stored in BigQuery, while the actual data files remain in **Google Cloud Storage (GCS)**.

When a query is executed, BigQuery reads the data directly from the GCS bucket.

### Question 8. Clustering best practices

**Question:**  
It is best practice in BigQuery to always cluster your data.

**Correct answer:**  
❌ **False**

**Explanation:**  
Clustering is **not always necessary** and should be used only when it matches your query patterns.

Clustering is most beneficial when:
- You frequently **filter**, **group**, or **order** by specific columns
- The table is **large enough** for clustering benefits to outweigh overhead

For small tables or tables that are rarely queried on specific columns, clustering may provide little to no benefit and can add unnecessary complexity.


### Question 9. Understanding table scans

**Question:**  
Write a `SELECT COUNT(*)` query on the **materialized table** you created.  
How many bytes does BigQuery estimate will be read? Why?

**Query:**
```sql
SELECT COUNT(*)
FROM `calm-snowfall-485503-b4.demo_dataset_ny_taxi.yellow_tripdata_2024`;

```


Answer (expected behavior):
BigQuery estimates that it will read the full size of the table (hundreds of MB).

Explanation:

COUNT(*) requires BigQuery to scan all rows in the table.

Even though BigQuery is a columnar database, COUNT(*) cannot rely on a single column or metadata alone for a regular (non-aggregated, non-partition-pruned) table.

As a result, BigQuery must read all partitions and all rows, leading to a full table scan.

Partitioning and clustering do not reduce bytes scanned for COUNT(*) unless the query includes filters that allow partition pruning.