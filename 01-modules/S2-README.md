# About

This module covers the various DAGs that will be used in the hands on lab.

## 1. Git clone the DAG and miscellaneous files

In cloud shell, scoped to the service project, clone the git repo

```
cd ~
git clone https://github.com/anagha-google/cloud-composer-setup-foundations.git
```

## 2. "Hello World" DAG directory

Navigate in cloud shell to-
```
cd ~/cloud-composer-setup-foundations/02-dags/00-hello-world-dag
ls -al
```

You should see the below-
```
drwxr-xr-x  3 ...  primarygroup   96 Feb  2 15:13 1-dag-base
drwxr-xr-x  5 ...  primarygroup  160 Feb  2 15:13 2-dag-gcf-orchestrated
drwxr-xr-x  5 ...  primarygroup  160 Feb  2 15:13 3-dag-pubsub-orchestrated
```


## 3. "Hello World" DAG Base

Navigate in cloud shell to-
```
cd ~/cloud-composer-setup-foundations/02-dags/00-hello-world-dag/1-dag-base
ls -al
```

You should see the below-
```
-rw-r--r--  1 ...  primarygroup  996 Feb  2 15:13 hello-world-dag.py
```

Cat the file and review it...<br>
This DAG just print "Hello World", for testing the environment, IAM permissions, permieter, network security and such.<br>

## 4. "Hello World" DAG triggered by Cloud Storage Event

Navigate in cloud shell to-
```
cd ~/cloud-composer-setup-foundations/02-dags/00-hello-world-dag/2-dag-gcf-orchestrated
ls -al
```

You should see the below-
```
-rw-r--r--  1 ...  primarygroup  2194 Feb  2 15:13 composer2_airflow_rest_api.py
-rw-r--r--  1 ...  primarygroup  1714 Feb  2 15:13 main.py
-rw-r--r--  1 ...  primarygroup    35 Feb  2 15:13 requirements.txt
```

Review each of the files for the Cloud Function-
main.py - calls composer2_airflow_rest_api that launches the Cloud Composer DAG

## 5. "Hello World" DAG triggered by Cloud Pub/Sub Event

Navigate in cloud shell to-
```
cd ~/cloud-composer-setup-foundations/02-dags/00-hello-world-dag/3-dag-pubsub-orchestrated
ls -al
```

You should see the below-
```
-rw-r--r--  1 ...  primarygroup  2194 Feb  2 15:13 composer2_airflow_rest_api.py
-rw-r--r--  1 ...  primarygroup  1714 Feb  2 15:13 main.py
-rw-r--r--  1 ...  primarygroup    35 Feb  2 15:13 requirements.txt
```

Review each of the files for the Cloud Function-
main.py - calls composer2_airflow_rest_api that launches the Cloud Composer DAG

## 6. Minimum viable ETL DAG

The "Minimum viable ETL DAG" uses a Cloud Dataflow template to read a CSV file in Cloud Storage, transform it using a JavaScript function, and loads/appends into a BigQuery table.
<br><br>
Navigate in cloud shell to-
```
cd ~/cloud-composer-setup-foundations/02-dags/01-min-viable-data-dag
ls -al
```

You should see the below-
```
drwxr-xr-x  3 akhanolkar  primarygroup   96 Feb  2 15:17 00-scripts
drwxr-xr-x  5 akhanolkar  primarygroup  160 Feb  2 15:20 01-source-files
```

Lets review the files under 01-source-files
```
ls -al 01-source-files
```

You should see-
```
-rw-r--r--  1 ...  primarygroup  211 Feb  2 15:20 inputFile.txt
-rw-r--r--  1 ...  primarygroup  539 Feb  2 15:20 jsonSchema.json
-rw-r--r--  1 ...  primarygroup  334 Feb  2 15:20 transformCSVtoJSON.js
```
- inputFile.txt has the source data
- jsonSchema.json is the schema file
- transformCSVtoJSON.js is a Javascript file that has a transformation function to be run by Cloud Dataflow
<br>

Now lets review the DAG script-
```
ls -al 00-scripts
```

You should see-
```
-rw-r--r--  1 ...  primarygroup  3541 Feb  2 15:16 min-viable-data-dag.py
```

Review the script ```min-viable-data-dag.py```. The DAG is explained in depth in the GCP Cloud Composer documentation.

