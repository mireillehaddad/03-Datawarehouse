--1️⃣ Authenticate with GCP
  ```bash
gcloud auth login
gcloud config set project calm-snowfall-485503-b4
```
--Verify:
```bash
gcloud config list
```
--2️⃣ Export BigQuery ML model to GCS

--BigQuery ML exports models in TensorFlow SavedModel format

```bash
bq --project_id=calm-snowfall-485503-b4 extract -m \
demo_dataset_ny_taxi.tip_model \
gs://calm-snowfall-485503-b4-terra-bucket/taxi_ml_model/tip_model
```
--This creates:


```bash
gs://calm-snowfall-485503-b4-terra-bucket/taxi_ml_model/tip_model/
```
--3️⃣ Download the model locally

```bash
mkdir -p /tmp/model
gsutil -m cp -r \
gs://calm-snowfall-485503-b4-terra-bucket/taxi_ml_model/tip_model \
/tmp/model
```

4️⃣ Prepare TensorFlow Serving directory structure

TensorFlow Serving requires a versioned directory:

```bash
mkdir -p serving_dir/tip_model/1
cp -r /tmp/model/tip_model/* serving_dir/tip_model/1
```

![
    
](serving_dir.png)

5️⃣ Pull TensorFlow Serving image

```bash
docker pull tensorflow/serving

```

6️⃣ Run TensorFlow Serving container

⚠️ Important fix:

Use $(pwd) not pwd

No space after target=
```bash
docker run -p 8501:8501 \
  --mount type=bind,source=$(pwd)/serving_dir/tip_model,target=/models/tip_model \
  -e MODEL_NAME=tip_model \
  -t tensorflow/serving &

```
Check logs:

```bash
docker logs $(docker ps -q --filter ancestor=tensorflow/serving)

```
7️⃣ Verify model is loaded

Open in browser:


```bash
http://localhost:8501/v1/models/tip_model

```


You should see model status = AVAILABLE.

8️⃣ Send prediction request

Your JSON is already correct


```bash
curl -X POST http://localhost:8501/v1/models/tip_model:predict \
-d '{
  "instances": [
    {
      "passenger_count": 1,
      "trip_distance": 12.2,
      "PULocationID": "193",
      "DOLocationID": "264",
      "payment_type": "2",
      "fare_amount": 20.4,
      "tolls_amount": 0.0
    }
  ]
}'


```

Expected response:

```bash
{
  "predictions": [ <predicted_tip_amount> ]
}

```

