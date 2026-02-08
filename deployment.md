## Google Cloud SDK setup + BigQuery ML model export (Codespaces)

### 1) Install Google Cloud SDK (gcloud, bq, gsutil)
From the Codespaces terminal:

```bash
curl -sSL https://sdk.cloud.google.com | bash
```

- Accepted the install prompts.
- When asked to update an rc file, I kept the default: `/home/codespace/.bashrc`
- This updated my PATH and enabled shell completion.

### 2) Reload the shell so PATH changes take effect
```bash
exec -l $SHELL
```

### 3) Verify tools are installed
```bash
gcloud --version
bq version
gsutil version
```

### 4) Authenticate to Google Cloud
```bash
gcloud auth login
```

Completed the browser login flow and authenticated as: `mireille.elhaddadwazen@gmail.com`

### 5) Set the active project
```bash
gcloud config set project calm-snowfall-485503-b4
```

**Note:** I received a warning that the project lacks an `environment` tag (best-practice notice).  
The project was still set successfully: `Updated property [core/project].`

### 6) Enable Cloud Resource Manager API (needed by gcloud config commands)
When running `gcloud config list`, I was prompted that the API was not enabled, so I enabled it:

```bash
gcloud config list
# Prompt appeared: API [cloudresourcemanager.googleapis.com] not enabled...
# I answered: Y
```

After enabling, the config showed:
- account = `mireille.elhaddadwazen@gmail.com`
- project = `calm-snowfall-485503-b4`

### 7) Attempted model export using the wrong project (failed as expected)
I first tried exporting using the sample project from course notes:

```bash
bq --project_id taxi-rides-ny extract -m nytaxi.tip_model gs://taxi_ml_model/tip_model
```

This failed with:
- Access Denied: no `bigquery.jobs.create` permission in project `taxi-rides-ny`

### 8) Exported the BigQuery ML model using my project and dataset (success)
I exported the model from my dataset:

- Project: `calm-snowfall-485503-b4`
- Dataset: `demo_dataset_ny_taxi`
- Model: `tip_model`
- GCS destination: `gs://calm-snowfall-485503-b4-terra-bucket/taxi_ml_model/tip_model`

```bash
bq --project_id=calm-snowfall-485503-b4 extract -m \
demo_dataset_ny_taxi.tip_model \
gs://calm-snowfall-485503-b4-terra-bucket/taxi_ml_model/tip_model
```

The export completed successfully (job status: DONE).

### Quick note about the long list of files 
That long list like:

- `google-cloud-sdk/lib/third_party/pytz/zoneinfo/...`

is normal — it’s part of the Google Cloud SDK installation (bundled Python + timezone data and third-party libraries). It does not indicate an error.


### 9)
```bash
mkdir /tmp/model
```

### 10)List the exported model in my bucket
```bash
gsutil ls gs://calm-snowfall-485503-b4-terra-bucket/taxi_ml_model/tip_model/
```

### 11)List the exported model in my bucket
```bash
gsutil ls gs://calm-snowfall-485503-b4-terra-bucket/taxi_ml_model/tip_model/
```