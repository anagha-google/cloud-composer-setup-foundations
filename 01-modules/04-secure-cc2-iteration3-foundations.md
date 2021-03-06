# About

This is the third iteration of security layered on and includes adding Private Service Connect on top of VPC-SC.

## 1.0. Prerequisites

Successful completion of prior modules.

## 2.0. About configuring Private Service Connect (PSC) 

As of the time this module was authored, Feb 2022, PSC could not be added to an existing Cloud Composer 2 and had to be configured at provision time. Therefore, delete the Cloud Composer cluster previously created and recreate with PSC enabled.
<br>
https://cloud.google.com/composer/docs/composer-2/configure-private-service-connect


## 3.0. Variables
In Cloud shell scoped to the service project/data analytics project, declare the below-
```
PROJECT_KEYWORD="thor"  # Replace with your keyword from module 1

ORG_ID=axxxolkar.altostrat.com                              #Replace with yours
ORG_ID_NBR=xxxxxxx                                      #Replace with yours

SVC_PROJECT_NUMBER=xxxxxxx                              #Replace with yours
SVC_PROJECT_ID=$PROJECT_KEYWORD-svc-proj                     #Data analytics service project

SHARED_VPC_HOST_PROJECT_ID=$PROJECT_KEYWORD-host-proj        #Shared VPC project - replace with yours
SHARED_VPC_HOST_PROJECT_NUMBER=xxxx                  #Shared VPC project - replace with yours

LOCATION=us-central1

ADMIN_UPN_FQN=admin@$ORG_ID #Replace with yours if its a different construct
SVC_PROJECT_UMSA="$PROJECT_KEYWORD-sa"
SVC_PROJECT_UMSA_FQN=$SVC_PROJECT_UMSA@$SVC_PROJECT_ID.iam.gserviceaccount.com

COMPOSER_ENV_NM=cc2-$PROJECT_KEYWORD-secure


SHARED_VPC_NETWORK_NM=$PROJECT_KEYWORD-shared-vpc
SHARED_VPC_NETWORK_FQN="projects/$SHARED_VPC_HOST_PROJECT_ID/global/networks/$SHARED_VPC_NETWORK_NM"
SHARED_VPC_CC2_SNET_NM="$PROJECT_KEYWORD-shared-cc2-snet"
SHARED_VPC_CC2_SNET_FQN="projects/$SHARED_VPC_HOST_PROJECT_ID/regions/$LOCATION/subnetworks/$SHARED_VPC_CC2_SNET_NM"
SHARED_VPC_CC2_SNET_CIDR_BLK='10.65.61.0/24'

GKE_CNTRL_PLN_CIDR_BLK='10.65.62.0/24' # GKE master
CC2_CIDR_BLK='10.65.63.0/24'  # Composer network
CSQL_CIDR_BLK='10.65.64.0/24' # Cloud SQL (Composer metastore)

OFFICE_CIDR=98.222.97.10/32 # Lab attendee's Public IP or your organization's office CIDR block for Airflow UI access
SERVERLESS_VPC_ACCESS_CONNECTOR_CIDR='10.70.0.0/28' # For event driven orchestration (GCF) to work

CC2_IMAGE_VERSION=composer-2.0.2-airflow-2.1.4  #composer-2.0.0-airflow-2.1.4
```

## 4.0. Provisioning
Provision "private" Cloud Composer 2 with shared VPC, VPC-SC and PSC<br>
From cloud shell in your service project/data analytics project, run the command below-

```
gcloud beta composer environments create $COMPOSER_ENV_NM \
    --image-version $CC2_IMAGE_VERSION \
    --labels env=demo,purpose=secure-cc2-demo \
    --location $LOCATION \
    --enable-private-environment \
    --network $SHARED_VPC_NETWORK_FQN \
    --connection-subnetwork $SHARED_VPC_CC2_SNET_FQN \
    --subnetwork $SHARED_VPC_CC2_SNET_FQN \
    --cluster-secondary-range-name composer-pods \
    --services-secondary-range-name composer-services \
    --master-ipv4-cidr $GKE_CNTRL_PLN_CIDR_BLK \
    --composer-network-ipv4-cidr $CC2_CIDR_BLK \
    --cloud-sql-ipv4-cidr $CSQL_CIDR_BLK \
    --service-account $SVC_PROJECT_UMSA_FQN \
    --enable-master-authorized-networks \
    --master-authorized-networks ${OFFICE_CIDR} \
    --web-server-allow-all
```

Note: Network ACLs for Airflow Webserver with Serverless VPC Connector pending clarification from the Cloud Composer product team. If supported, the command above, can be modified to-

```
gcloud beta composer environments create $COMPOSER_ENV_NM \
    --image-version $CC2_IMAGE_VERSION \
    --labels env=demo,purpose=secure-cc2-demo \
    --location $LOCATION \
    --enable-private-environment \
    --network $SHARED_VPC_NETWORK_FQN \
    --connection-subnetwork $SHARED_VPC_CC2_SNET_FQN \
    --subnetwork $SHARED_VPC_CC2_SNET_FQN \
    --cluster-secondary-range-name composer-pods \
    --services-secondary-range-name composer-services \
    --master-ipv4-cidr $GKE_CNTRL_PLN_CIDR_BLK \
    --composer-network-ipv4-cidr $CC2_CIDR_BLK \
    --cloud-sql-ipv4-cidr $CSQL_CIDR_BLK \
    --service-account $SVC_PROJECT_UMSA_FQN \
    --enable-master-authorized-networks \
    --master-authorized-networks ${OFFICE_CIDR} \
    --web-server-allow-ip ip_range=${OFFICE_CIDR},description="Office CIDR" \
    --web-server-allow-ip ip_range=${SERVERLESS_VPC_ACCESS_CONNECTOR_CIDR},description="Serverless VPC Connector subnet"
```

<hr>

## 5.0. Testing

Validate the setup by running all the DAGs, manually and with event driven orchestraion. 

## 6.0. Housekeeping
This concludes the module. Delete the projects created, upon completion.
