# About

This section covers provisioning a secure Cloud Composer 2 environment but without VPC-SC and PSC.<br>
This entire module is run in the service project/data analytics project.

## 1. Dependencies

Completion of the prior module.

## 2. Variables used in the project

In Cloud shell scoped to the service project/data analytics project, e2e-demo-indra in the author's case, declare the below-
```
DA_PROJECT_ID=e2e-demo-indra
UMSA="indra-sa"
UMSA_FQN=$UMSA@$DA_PROJECT_ID.iam.gserviceaccount.com
ADMIN_FQ_UPN="admin@akhanolkar.altostrat.com"

COMPOSER_ENV_NM=cc2-indra-secure
LOCATION=us-central1

DA_PROJECT_NUMBER=914583619622
DA_PROJECT_ID=e2e-demo-indra
SHARED_VPC_PROJECT_ID=$DA_PROJECT_ID"-shared"

SHARED_VPC_NETWORK_NM=indra-vpc-shared
SHARED_VPC_NETWORK_FQN="projects/$SHARED_VPC_PROJECT_ID/global/networks/$SHARED_VPC_NETWORK_NM"
SHARED_VPC_CC2_SNET_NM="indra-composer2-snet-shared"
SHARED_VPC_CC2_SNET_FQN="projects/$SHARED_VPC_PROJECT_ID/regions/$LOCATION/subnetworks/$SHARED_VPC_CC2_SNET_NM"
SHARED_VPC_CC2_SNET_CIDR_BLK='10.65.61.0/24'
CC2_PODS_CIDR_BLK='10.66.0.0/16' # Composer pods, ensure sufficient, especially for autoscale
CC2_SVCS_CIDR_BLK='10.67.0.0/16' # Composer services, ensure sufficient, especially for autoscale
GKE_CNTRL_PLN_CIDR_BLK='10.65.62.0/24' # GKE master
CC2_CIDR_BLK='10.65.63.0/24'  # Composer network
CSQL_CIDR_BLK='10.65.64.0/24' # Cloud SQL (Composer metastore)

OFFICE_CIDR=98.222.97.10/32 # Lab attendee's Public IP or your organization's office CIDR block for VPC-SC
```


## 3. Provision "private" Cloud Composer 2 with shared VPC & VPC-SC

From cloud shell in your service project/data analytics project, run the command below-

```
gcloud beta composer environments create $COMPOSER_ENV_NM \
    --image-version "composer-2.0.0-airflow-2.1.4" \
    --labels env=demo,purpose=secure-cc2-demo \
    --location $LOCATION \
    --enable-private-environment \
    --network $SHARED_VPC_NETWORK_FQN \
    --subnetwork $SHARED_VPC_CC2_SNET_FQN \
    --cluster-ipv4-cidr $CC2_PODS_CIDR_BLK \
    --services-ipv4-cidr $CC2_SVCS_CIDR_BLK \
    --master-ipv4-cidr $GKE_CNTRL_PLN_CIDR_BLK \
    --composer-network-ipv4-cidr $CC2_CIDR_BLK \
    --cloud-sql-ipv4-cidr $CSQL_CIDR_BLK \
    --service-account $UMSA_FQN \
    --web-server-allow-ip ip_range=${OFFICE_CIDR},description="Office CIDR"   
```

### References:
Securing Airflow Web UI: https://cloud.google.com/composer/docs/composer-2/create-environments#web-server-access<br>
