# About

This section covers provisioning a secure Cloud Composer 2 environment *but without* VPC-SC and PSC.<br>
This entire module is run in the service project (data analytics project).

<hr>

## 1. Dependencies

Completion of the prior module.

<hr>

## 2. Variables used in the project

In Cloud shell scoped to the service project, declare the below-
```
PROJECT_KEYWORD="thor"  # Replace with your keyword from module 1

#Replace with yours
ORG_ID=akaxxxar.altostrat.com                              
ORG_ID_NBR=xxxxxxxx                                      

#Replace with yours
SVC_PROJECT_NUMBER=5xxxx                              
SVC_PROJECT_ID=$PROJECT_KEYWORD-svc-proj                     

#Shared VPC project - replace with yours
SHARED_VPC_HOST_PROJECT_ID=$PROJECT_KEYWORD-host-proj        
SHARED_VPC_HOST_PROJECT_NUMBER=xxxxx                 


UMSA="$PROJECT_KEYWORD-sa"
UMSA_FQN=$UMSA@$SVC_PROJECT_ID.iam.gserviceaccount.com

#Replace with yours
ADMIN_FQ_UPN="admin@akhanolkar.altostrat.com"               

COMPOSER_ENV_NM=cc2-$PROJECT_KEYWORD-secure
LOCATION=us-central1


SHARED_VPC_NETWORK_NM=$PROJECT_KEYWORD-shared-vpc
SHARED_VPC_NETWORK_FQN="projects/$SHARED_VPC_HOST_PROJECT_ID/global/networks/$SHARED_VPC_NETWORK_NM"
SHARED_VPC_CC2_SNET_NM="$PROJECT_KEYWORD-shared-cc2-snet"
SHARED_VPC_CC2_SNET_FQN="projects/$SHARED_VPC_HOST_PROJECT_ID/regions/$LOCATION/subnetworks/$SHARED_VPC_CC2_SNET_NM"
SHARED_VPC_CC2_SNET_CIDR_BLK='10.65.61.0/24'

# GKE master
GKE_CNTRL_PLN_CIDR_BLK='10.65.62.0/24' 
# Composer network
CC2_CIDR_BLK='10.65.63.0/24' 
# Cloud SQL (Composer metastore)****
CSQL_CIDR_BLK='10.65.64.0/24' 

# Lab attendee's Public IP or your organization's office CIDR block for Airflow UI access
OFFICE_CIDR=98.222.97.10/32 

# For event driven orchestration (GCF) to work
SERVERLESS_VPC_ACCESS_CONNECTOR_CIDR='10.70.0.0/28' 

CC2_IMAGE_VERSION=composer-2.0.2-airflow-2.1.4  
```

<hr>

## 3. Provision "private" Cloud Composer 2 with shared VPC

From cloud shell in your service project/data analytics project, run the command below-

```
gcloud beta composer environments create $COMPOSER_ENV_NM \
    --image-version $CC2_IMAGE_VERSION \
    --labels env=demo,purpose=secure-cc2-demo \
    --location $LOCATION \
    --enable-private-environment \
    --network $SHARED_VPC_NETWORK_FQN \
    --subnetwork $SHARED_VPC_CC2_SNET_FQN \
    --cluster-secondary-range-name composer-pods \
    --services-secondary-range-name composer-services \
    --master-ipv4-cidr $GKE_CNTRL_PLN_CIDR_BLK \
    --composer-network-ipv4-cidr $CC2_CIDR_BLK \
    --cloud-sql-ipv4-cidr $CSQL_CIDR_BLK \
    --service-account $UMSA_FQN \
    --enable-master-authorized-networks \
    --master-authorized-networks ${OFFICE_CIDR} \
    --web-server-allow-all
```


Once supported by the product, we can restrict the Airflow webserver to specific CIDRs including that of the serverless VPC Connector subnet with this provisioning command-
```
gcloud beta composer environments create $COMPOSER_ENV_NM \
    --image-version $CC2_IMAGE_VERSION \
    --labels env=demo,purpose=secure-cc2-demo \
    --location $LOCATION \
    --enable-private-environment \
    --network $SHARED_VPC_NETWORK_FQN \
    --subnetwork $SHARED_VPC_CC2_SNET_FQN \
    --cluster-secondary-range-name composer-pods \
    --services-secondary-range-name composer-services \
    --master-ipv4-cidr $GKE_CNTRL_PLN_CIDR_BLK \
    --composer-network-ipv4-cidr $CC2_CIDR_BLK \
    --cloud-sql-ipv4-cidr $CSQL_CIDR_BLK \
    --service-account $UMSA_FQN \
    --enable-master-authorized-networks \
    --master-authorized-networks ${OFFICE_CIDR} \
    --web-server-allow-ip ip_range=${OFFICE_CIDR},description="Office CIDR" \
    --web-server-allow-ip ip_range=${SERVERLESS_VPC_ACCESS_CONNECTOR_CIDR},description="Serverless VPC Connector subnet"
```

<hr>

## 4. Pictorial walk through of Cloud Composer environment

### 4.1. Navigating to Cloud Composer

![CC-1](../00-images/2b-01-navigate.png)

### 4.2. Landing page

![CC-2](../00-images/2b-02-landing.png)

### 4.3. Monitoring 

![CC-3](../00-images/2b-03-monitoring.png)

### 4.4. Logs

![CC-4](../00-images/2b-04-logs.png)

### 4.5. Environment Configuration 

![CC-5a](../00-images/2b-05-ec.png)

![CC-5b](../00-images/2b-05-ec-2.png)

### 4.6. Airflow Configuration Overrides 

![CC-6](../00-images/2b-06-ac.png)

### 4.7. Environment Variables 

![CC-7](../00-images/2b-07-ev.png)

### 4.8. Labels

![CC-8](../00-images/2b-08-lbl.png)

### 4.9. Pypi Packages 

![CC-9](../00-images/2b-09-pypi.png)

### 4.10. Airflow website

![CC-10](../00-images/2b-10-af-uri.png)

![CC-10a](../00-images/2b-11-af.png)

<hr>

## 5. Pictorial walk through of the underlying Google Kubernetes Engine environment

### 5.1. Navigating

![gke-1](../00-images/2b-12-k8s.png)

### 5.2. Landing page

![gke-2](../00-images/2b-13-k8s.png)

### 5.3. Cluster attributes 

![gke-3a](../00-images/2b-14-k8s.png)

![gke-3b](../00-images/2b-15-k8s.png)

![gke-3c](../00-images/2b-16-k8s.png)

![gke-3d](../00-images/2b-17-k8s.png)

![gke-3e](../00-images/2b-18-k8s.png)

<hr>


## 6. What about other dependencies provisioned?

### 6.1. Metastore
The underlying Cloud SQL used as metastore is not exposed. 


### 6.2. Cloud Storage
A single Cloud Storage is auto-created when the environment is provisioned.

![gcs-1](../00-images/2b-20-gcs.png)

![gcs-2](../00-images/2b-21-gcs.png)



### 6.3. Cloud Pub/Sub
Cloud Pub/Sub toics are auto-created and used under the hood

![ps-1](../00-images/2b-22-pubsub.png)

<hr>
<br>


## 7.0. Airflow User Setup in the service project

In this step, we wll add the User Managed Service Account - zeus-sa to the Airflow database, so it can access the Airflow web components via Cloud Functions call in subsetquent modules.

<br>
a) First, lets check the users already configured in the Airflow database. Run this in the service project-
```
gcloud composer environments run $COMPOSER_ENV_NM --location=$LOCATION users -- list
```

Here is the author's output-
```
akhanolkar-macbookpro2% gcloud composer environments run $COMPOSER_ENV_NM --location=$LOCATION users -- list
kubeconfig entry generated for us-central1-cc2-thor-secure-d18c82d4-gke.
Executing within the following Kubernetes cluster namespace: composer-2-0-2-airflow-2-1-4-d18c82d4
id | username         | email            | first_name        | last_name | roles
===+==================+==================+===================+===========+======
1  | accounts.google. | admin@akhanolkar | admin@akhanolkar. | -         | Op   
   | com:111645786868 | .altostrat.com   | altostrat.com     |           |      
   | 869111335        |                  |                   |           |      

```

b) Next, lets get the numeric ID of the UMSA for our project-

```
UMSA_NUM_ID=`gcloud iam service-accounts describe $UMSA_FQN --format="value(oauth2ClientId)"`
```

<br>
c) Lets add the UMSA to the Airlow Users table-
```
gcloud composer environments run $COMPOSER_ENV_NM --location=$LOCATION users -- create --use-random-password --username "accounts.google.com:$UMSA_NUM_ID" --role Op --email  $UMSA_FQN -f Service -l Account
```
<br>

d) Validate the addition-
```
gcloud composer environments run $COMPOSER_ENV_NM --location=$LOCATION users -- list
```

Author's output-
```
akhanolkar-macbookpro2% gcloud composer environments run $COMPOSER_ENV_NM --location=$LOCATION users -- list
kubeconfig entry generated for us-central1-cc2-thor-secure-d18c82d4-gke.
Executing within the following Kubernetes cluster namespace: composer-2-0-2-airflow-2-1-4-d18c82d4
id | username         | email            | first_name        | last_name | roles
===+==================+==================+===================+===========+======
1  | accounts.google. | admin@akhanolkar | admin@akhanolkar. | -         | Op   
   | com:111645786868 | .altostrat.com   | altostrat.com     |           |      
   | 869111335        |                  |                   |           |      
2  | accounts.google. | thor-sa@thor-svc | Service           | Account   | Op   
   | com:113649389075 | -proj.iam.gservi |                   |           |      
   | 672365994        | ceaccount.com    |                   |           | 
```

<hr>
<br>

This concludes the module, proceed to the [next module](02c-secure-cc2-iteration1-HWD-Base.md).


