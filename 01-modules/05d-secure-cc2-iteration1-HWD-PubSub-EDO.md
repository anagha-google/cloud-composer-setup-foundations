# About

This module builds on the "Hello World" exercise, by adding the orchestration element to it.<br>
Specifically, Pub/Sub message event driven orchestration.<br>


## 1.0. Create a Google Pub/Sub topic

Note: We already enabled the Pub/Sub API in the prerequisites module. <br>
From cloud shell, run the commands below-

a) The variables
```
SVC_PROJECT_ID=zeus-svc-proj
SHARED_VPC_HOST_PROJECT_ID=zeus-host-proj 

UMSA="zeus-sa"
UMSA_FQN=$UMSA@$SVC_PROJECT_ID.iam.gserviceaccount.com

COMPOSER_ENV_NM=cc2-zeus-secure
LOCATION=us-central1

PUBSUB_TRIGGER_TOPIC=cc2-hw-trigger-topic
DAG_ID=hello_world_dag
```

b) Create a Pub/Sub topic
```
gcloud pubsub topics create $PUBSUB_TRIGGER_TOPIC
```

c) Check the Cloud Console UI and browse through the various tabs and configuration<br>

Navigate to Cloud Pub/Sub UI<br>
![01-02-10](../00-images/01-02-10.png)
<br><br><br>

Review the Pub/Sub topic listing
![01-02-11](../00-images/01-02-11.png)
<br><br><br>

Browse through the Pub/Sub topic UI
![01-02-12](../00-images/01-02-12.png)
<br><br><br>

## 2.0. Get the Airflow Web URL

```
AIRFLOW_URI=`gcloud composer environments describe $COMPOSER_ENV_NM \
    --location $LOCATION \
    --format='value(config.airflowUri)'`
```

Validate:
```
echo $AIRFLOW_URI
https://e2XXXXXXX09e8bf9-dot-us-central1.composer.googleusercontent.com
```

## 3.0. Review the Airflow DAG executor script

In cloud shell, navigate to the scripts directory for the exercise-
```
cd ~/e2e-demo-indra/03-Cloud-Composer2/01-hello-world-dag/00-scripts/3-dag-pubsub-orchestrated/
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

2. Replace DAG_NAME_TO_BE_REPLACED in main.py with your env specific value
```
sed -i "s|DAG_ID_TO_BE_REPLACED|$DAG_ID|g" main.py
```

3. Validate
```
cat main.py
```

You should see the actual Airflow URI and the DAG ID

## 7.0. Deploy the Google Cloud Function (GCF) to run as UMSA

Takes approximately 2 minutes.

```
gcloud functions deploy cc2_hw_pubsub_trigger_fn \
--entry-point trigger_dag_gcf \
--trigger-topic $PUBSUB_TRIGGER_TOPIC \
--runtime python39 \
--vpc-connector projects/$SHARED_VPC_HOST_PROJECT_ID/locations/$LOCATION/connectors/zeus-gcf-vpc-cnnctr \
--service-account=${UMSA_FQN}
```

a) In the cloud console, navigate to Cloud Functions-

![01-02-13](../00-images/01-02-13.png)
<br><br><br>

b) Gp back to the Cloud Pub/Sub UI and notice that the deployment of the Pub/Sub topic triggered GCF created a Pub/Sub subscription

![01-02-14](../00-images/01-02-14.png)
<br><br><br>



## 8.0.Test the function from cloud shell

```
CURRENT_TIME=`date -d "-6 hours"`
gcloud pubsub topics publish $PUBSUB_TRIGGER_TOPIC --message "$CURRENT_TIME"
```

Go to the Cloud Function Logs, in the cloud console and check for errors..

![01-02-15](../00-images/01-02-15.png)
<br>

And then go to Airflow web UI and click on the DAG node, and look at the logs...
![01-02-16](../00-images/01-02-16.png)
<br>

Publish multiple messages to the Pub/Sub topic and explore DAG runs in the Airflow UI...
![01-02-17](../00-images/01-02-17.png)
<br>

## 9.0. Lets do a quick review of permissions for the major identities in scope for this demo

Go to the Cloud Console and navigate to the IAM -> IAM & Admin and ensure you check the "Include Google Provided Role Grants". Screenshots of what you should expect are below. 

## 9.0.1. The lab attendee permissions
![01-02-06](../00-images/01-02-06.png)
<br>

## 9.0.2. The UMSA permissions
![01-02-07](../00-images/01-02-07.png)
<br>

## 9.0.3. The Cloud Composer Service Agent Account permissions
![01-02-08](../00-images/01-02-08.png)
<br>

## 9.0.4. The various Google Managed Default Service Accounts
![01-02-09](../00-images/01-02-09.png)
<br>

