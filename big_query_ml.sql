-- SELECT THE COLUMNS YOU'RE INTERESTED IN
SELECT
  passenger_count,
  trip_distance,
  PULocationID,
  DOLocationID,
  payment_type,
  fare_amount,
  tolls_amount,
  tip_amount
FROM `calm-snowfall-485503-b4.demo_dataset_ny_taxi.yellow_tripdata_partitioned`
WHERE fare_amount != 0;


-- CREATE A ML TABLE WITH APPROPRIATE TYPES
-- (Cast IDs + payment_type to STRING; keep numerics as numeric)
CREATE OR REPLACE TABLE `calm-snowfall-485503-b4.demo_dataset_ny_taxi.yellow_tripdata_ml` AS
SELECT
  CAST(passenger_count AS INT64) AS passenger_count,
  CAST(trip_distance AS FLOAT64) AS trip_distance,
  CAST(PULocationID AS STRING) AS PULocationID,
  CAST(DOLocationID AS STRING) AS DOLocationID,
  CAST(payment_type AS STRING) AS payment_type,
  CAST(fare_amount AS FLOAT64) AS fare_amount,
  CAST(tolls_amount AS FLOAT64) AS tolls_amount,
  CAST(tip_amount AS FLOAT64) AS tip_amount
FROM `calm-snowfall-485503-b4.demo_dataset_ny_taxi.yellow_tripdata_partitioned`
WHERE fare_amount != 0
  AND tip_amount IS NOT NULL;


-- CREATE MODEL WITH DEFAULT SETTINGS
CREATE OR REPLACE MODEL `calm-snowfall-485503-b4.demo_dataset_ny_taxi.tip_model`
OPTIONS (
  model_type = 'linear_reg',
  input_label_cols = ['tip_amount'],
  data_split_method = 'AUTO_SPLIT'
) AS
SELECT
  *
FROM `calm-snowfall-485503-b4.demo_dataset_ny_taxi.yellow_tripdata_ml`;


-- CHECK FEATURES
SELECT *
FROM ML.FEATURE_INFO(MODEL `calm-snowfall-485503-b4.demo_dataset_ny_taxi.tip_model`);


-- EVALUATE THE MODEL
SELECT *
FROM ML.EVALUATE(
  MODEL `calm-snowfall-485503-b4.demo_dataset_ny_taxi.tip_model`,
  (
    SELECT *
    FROM `calm-snowfall-485503-b4.demo_dataset_ny_taxi.yellow_tripdata_ml`
  )
);


-- PREDICT
SELECT *
FROM ML.PREDICT(
  MODEL `calm-snowfall-485503-b4.demo_dataset_ny_taxi.tip_model`,
  (
    SELECT *
    FROM `calm-snowfall-485503-b4.demo_dataset_ny_taxi.yellow_tripdata_ml`
  )
);


-- PREDICT AND EXPLAIN
SELECT *
FROM ML.EXPLAIN_PREDICT(
  MODEL `calm-snowfall-485503-b4.demo_dataset_ny_taxi.tip_model`,
  (
    SELECT *
    FROM `calm-snowfall-485503-b4.demo_dataset_ny_taxi.yellow_tripdata_ml`
  ),
  STRUCT(3 AS top_k_features)
);


-- HYPERPARAMETER TUNING
CREATE OR REPLACE MODEL `calm-snowfall-485503-b4.demo_dataset_ny_taxi.tip_hyperparam_model`
OPTIONS (
  model_type = 'linear_reg',
  input_label_cols = ['tip_amount'],
  data_split_method = 'AUTO_SPLIT',
  num_trials = 5,
  max_parallel_trials = 2,
  l1_reg = HPARAM_RANGE(0, 20),
  l2_reg = HPARAM_CANDIDATES([0, 0.1, 1, 10])
) AS
SELECT
  *
FROM `calm-snowfall-485503-b4.demo_dataset_ny_taxi.yellow_tripdata_ml`;
