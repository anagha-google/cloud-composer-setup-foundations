# About

This module builds on the "Hello World" exercise, by adding the orchestration element to it.<br>
Specifically, GCS bucket event driven orchestration.<br>

FIRST and foremost - read this [GCP documentation](https://cloud.google.com/composer/docs/composer-2/triggering-with-gcf) to get an understanding of what we are about to attempt. Start with step 1, once done.

## Duration 
~ 30 minutes or less

## Skill Level
Medium

## Goal
The attendee should be able to trigger a DAG execution in response to a GCS event.


## 1.0. Create a GCS trigger bucket

From cloud shell, run the commands below-

a) The variables
```
SVC_PROJECT_ID=zeus-svc-proj
UMSA="zeus-sa"
UMSA_FQN=$UMSA@$SVC_PROJECT_ID.iam.gserviceaccount.com
COMPOSER_ENV_NM=cc2-zeus-secure
LOCATION=us-central1
GCF_TRIGGER_BUCKET_FQN=gs://cc2-hw-trigger-bucket
DAG_ID=hello_world_dag
```

b) Create a bucket
```
gsutil mb -p $SVC_PROJECT_ID -c STANDARD -l $LOCATION -b on $GCF_TRIGGER_BUCKET_FQN
```

## 2.0. Get the Airflow Web URL

```
AIRFLOW_URI=`gcloud composer environments describe $COMPOSER_ENV_NM \
    --location $LOCATION \
    --format='value(config.airflowUri)'`
```

Validate:
```
echo $AIRFLOW_URI
```

The author's result-
```
https://e2XXXXXXX09e8bf9-dot-us-central1.composer.googleusercontent.com
```

## 3.0. Review the Airflow DAG executor script

In cloud shell, navigate to the scripts directory for the exercise-
```
cd ~/e2e-demo-indra/03-Cloud-Composer2/01-hello-world-dag/00-scripts/2-dag-gcf-orchestrated/
```

Open and review the script below-
```
cat composer2_airflow_rest_api.py
```

Do not change any variables.<br>
The Cloud Function we will author, imports this file from the main.py file.

## 4.0. Review the Python dependencies file

Open and review the script below-
```
cat requirements.txt
```

## 5.0. Review the GCF main python file

Open and review the script below-
```
cat main.py
```

Notice that there are two variables to be replaced-<br>
AIRFLOW_URI_TO_BE_REPLACED<br>
and<br>
DAG_ID_TO_BE_REPLACED<br>

## 6.0. Update the GCF main python file

1. Replace WEB_SERVER_URL_TO_BE_REPLACED in main.py with your env specific value

```
sed -i "s|AIRFLOW_URI_TO_BE_REPLACED|$AIRFLOW_URI|g" main.py
```
If you are on a Mac with zsh-
```
sed -i '' "s|AIRFLOW_URI_TO_BE_REPLACED|$AIRFLOW_URI|g" main.py
```

2. Replace DAG_NAME_TO_BE_REPLACED in main.py with your env specific value
```
sed -i "s|DAG_ID_TO_BE_REPLACED|$DAG_ID|g" main.py
```
If you are on a Mac with zsh-
```
sed -i '' "s|DAG_ID_TO_BE_REPLACED|$DAG_ID|g" main.py
```

3. Validate
```
cat main.py
```

You should see the actual Airflow URI and the DAG ID replaced in the code

```
def trigger_dag_gcf(data, context=None):
    """
    ....
    web_server_url = (
        'https://3e84aaa5xxxx5f41d7177bd49-dot-us-central1.composer.googleusercontent.com'
    )
    # Replace with the ID of the DAG that you want to run.
    dag_id = 'hello_world_dag'

    ...
```


## 7.0. Deploy the Google Cloud Function (GCF) to run as UMSA

Takes approximately 2 minutes.

```
USE_EXPERIMENTAL_API='False'


gcloud functions deploy cc2_hw_gcs_trigger_fn \
--entry-point trigger_dag_gcf \
--trigger-resource $GCF_TRIGGER_BUCKET_FQN \
--trigger-event google.storage.object.finalize \
--runtime python39   \
--set-env-vars USE_EXPERIMENTAL_API=${USE_EXPERIMENTAL_API} \
--service-account=${UMSA_FQN}
```

a) In the cloud console, navigate to Cloud Functions-

![01-02-01](../00-images/01-02-01.png)
<br><br><br>

b) Click on the deployed function
![01-02-02](../00-images/01-02-02.png)
<br><br><br>

c) Review the various tabs
![01-02-03](../00-images/01-02-03.png)


## 8.0.Test the function from cloud shell

### 8.0.1. Create a trigger file in GCS
```
touch dummy.txt
gsutil cp dummy.txt $GCF_TRIGGER_BUCKET_FQN
rm dummy.txt
```

### 8.0.2. Validate successful GCF execution

Go to the Cloud Function Logs, in the cloud console and check for errors..

![01-02-04](../00-images/01-02-04.png)
<br>

And then go to Airflow web UI and click on the DAG node, and look at the logs...
![01-02-05](../01-images/01-02-05.png)
<br>

<hr>
This concludes the lab module.
