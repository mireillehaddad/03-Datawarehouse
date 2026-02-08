IN GCP Big Query:

```bash

Create the external Yellow Taxi table
CREATE OR REPLACE EXTERNAL TABLE
  `calm-snowfall-485503-b4.demo_dataset_ny_taxi.external_yellow_tripdata`
OPTIONS (
  format = 'CSV',
  uris = [
    'gs://calm-snowfall-485503-b4-terra-bucket/yellow_tripdata_2019-*.csv',
    'gs://calm-snowfall-485503-b4-terra-bucket/yellow_tripdata_2020-*.csv'
  ],
  skip_leading_rows = 1
);

```

```bash

SELECT COUNT(*) 
FROM `calm-snowfall-485503-b4.demo_dataset_ny_taxi.external_yellow_tripdata`;

```


```bash
SELECT * 
FROM `calm-snowfall-485503-b4.demo_dataset_ny_taxi.external_yellow_tripdata`  limit 10;
```
```bash

CREATE OR REPLACE TABLE
  `calm-snowfall-485503-b4.demo_dataset_ny_taxi.yellow_tripdata_non_partitioned` AS
SELECT *
FROM
  `calm-snowfall-485503-b4.demo_dataset_ny_taxi.external_yellow_tripdata`;
  ```

  ```bash

CREATE OR REPLACE TABLE
  `calm-snowfall-485503-b4.demo_dataset_ny_taxi.yellow_tripdata_partitioned`
PARTITION BY
  DATE(tpep_pickup_datetime) AS
SELECT *
FROM
  `calm-snowfall-485503-b4.demo_dataset_ny_taxi.external_yellow_tripdata`;
  ```
 ```bash

SELECT COUNT(*)
FROM `calm-snowfall-485503-b4.demo_dataset_ny_taxi.yellow_tripdata_partitioned`
WHERE DATE(tpep_pickup_datetime) = '2019-01-15';
  ```
 ```bash

-- Impact of partition
SELECT DISTINCT VendorID
FROM `calm-snowfall-485503-b4.demo_dataset_ny_taxi.yellow_tripdata_non_partitioned`
WHERE DATE(tpep_pickup_datetime) BETWEEN '2019-06-01' AND '2019-06-30';
  ```

 ```bash

-- Impact of partition
  SELECT DISTINCT VendorID
FROM `calm-snowfall-485503-b4.demo_dataset_ny_taxi.yellow_tripdata_partitioned`
WHERE DATE(tpep_pickup_datetime) BETWEEN '2019-06-01' AND '2019-06-30';
  ```

 ```bash

SELECT
  table_name,
  partition_id,
  total_rows
FROM `calm-snowfall-485503-b4.demo_dataset_ny_taxi.INFORMATION_SCHEMA.PARTITIONS`
WHERE table_name = 'yellow_tripdata_partitioned'
ORDER BY total_rows DESC;
  ```

 ```bash


  CREATE OR REPLACE TABLE
  `calm-snowfall-485503-b4.demo_dataset_ny_taxi.yellow_tripdata_partitioned_clustered`
PARTITION BY DATE(tpep_pickup_datetime)
CLUSTER BY VendorID AS
SELECT *
FROM
  `calm-snowfall-485503-b4.demo_dataset_ny_taxi.external_yellow_tripdata`;
  ```
 ```bash
-- Query scans ~1.1 GB (partitioned, not clustered)
SELECT COUNT(*) AS trips
FROM `calm-snowfall-485503-b4.demo_dataset_ny_taxi.yellow_tripdata_partitioned`
WHERE DATE(tpep_pickup_datetime) BETWEEN '2019-06-01' AND '2020-12-31'
  AND VendorID = 1;

 ```

  ```bash
-- Query scans ~864.5 MB (partitioned + clustered)
SELECT COUNT(*) AS trips
FROM `calm-snowfall-485503-b4.demo_dataset_ny_taxi.yellow_tripdata_partitioned_clustered`
WHERE DATE(tpep_pickup_datetime) BETWEEN '2019-06-01' AND '2020-12-31'
  AND VendorID = 1;

 ```