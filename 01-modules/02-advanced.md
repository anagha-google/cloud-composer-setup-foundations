# About

This module covers advanced networking, for data services of data analytics deployments that mimic product setup at enterprise customers.

## Dependencies
Some aspects detailed below are dependent on existence of a data analytics (DA) project (in the author's case, the DA project name is "e2-demo-indra").

## 0. Create a project for "Shared VPC"called e2e-demo-indra-shared

Create a new project for the shared VPC

## 1. Variables in the "Shared VPC" project

In cloud shell scoped to the shared VPC project, paste the following variables after updating the same to match your environment-
```

ORG_ID=akhanolkar.altostrat.com #Replace with yours
ORG_ID_NBR=236589261571 #Replace with yours

DA_PROJECT_NUMBER=914583619622
DA_PROJECT_ID=e2e-demo-indra #Data analytics project

SHARED_VPC_HOST_PROJECT_ID=$DA_PROJECT_ID-shared #Shared VPC project

PROJECT_LOCATION=us-central1

ADMIN_UPN_FQN=admin@$ORG_ID #Replace with yours if its a different construct
DA_PROJECT_UMSA="indra-sa"
DA_PROJECT_UMSA_FQN=$DA_PROJECT_UMSA@$DA_PROJECT_ID.iam.gserviceaccount.com


SHARED_VPC_NETWORK_NM=indra-vpc-shared
SHARED_VPC_FQN="projects/e2e-demo-indra-shared/global/networks/indra-vpc-shared"
SHARED_VPC_CC2_SNET_NM="indra-composer2-snet-shared"
SHARED_VPC_CC2_SNET_FQN="projects/e2e-demo-indra-shared/regions/us-central1/subnetworks/indra-composer2-snet-shared"

SHARED_VPC_CC2_SNET_CIDR_BLK='10.65.61.0/24' # Number of GKE nodes and ILBs available 
CC2_PODS_CIDR_BLK='10.66.0.0/16' # Composer pods, ensure sufficient, especially for autoscale
CC2_SVCS_CIDR_BLK='10.67.0.0/16' # Composer pods, ensure sufficient, especially for autoscale
GKE_CNTRL_PLN_CIDR_BLK='10.65.62.0/24' 
CC2_CIDR_BLK='10.65.63.0/24' 
CSQL_CIDR_BLK='10.65.64.0/24'

LOCATION=us-central1
```
## 2. Enable Google APIs in the shared VPC host project

```
gcloud services enable container.googleapis.com --project $SHARED_VPC_HOST_PROJECT_ID
gcloud services enable orgpolicy.googleapis.com --project $SHARED_VPC_HOST_PROJECT_ID
```

## 3. Grant IAM role to admin, to create a "Shared VPC"

In cloud shell scoped to the shared VPC project, run the below:
```
gcloud organizations add-iam-policy-binding $ORG_ID_NBR \
  --member=user:$ADMIN_UPN_FQN \
  --role="roles/compute.xpnAdmin"
```

## 4. Enable shared VPC for the "Shared VPC" project

In cloud shell scoped to the shared VPC project, run the below:
```
gcloud compute shared-vpc enable $SHARED_VPC_HOST_PROJECT_ID
```

## 5. Associate your data analytics project with the "Shared VPC" project

In cloud shell scoped to the shared VPC project, run the below:
```
gcloud compute shared-vpc associated-projects add $DA_PROJECT_ID \
    --host-project $SHARED_VPC_HOST_PROJECT_ID
```

## 6. Review IP range considerations for Cloud Composer 2

A core requirement here is to ensure there is no CIDR range overlap between your ranges and the Google services
<br>Review the documentation [here](
https://cloud.google.com/composer/docs/composer-2/configure-private-ip#step_1_check_network_requirements)


## 7. Create a VPC in the "shared VPC" project

```
gcloud compute networks create $SHARED_VPC_NETWORK_NM \
--project=$SHARED_VPC_HOST_PROJECT_ID \
--subnet-mode=custom \
--mtu=1460 \
--bgp-routing-mode=regional
```

## 8. Create subnet for secure Cloud Composer 2

Per the docs, these are considerations-
```
To create a Private IP environment, we need to have the following setup:<br>
We need five secondary IP ranges for Composer 2-<br>
- Secondary IP range for pods<br>
- Secondary IP range for services<br>
- GKE Control Plane IP range<br>
- Cloud Composer network IP range<br>
- Cloud SQL IP range<br>


Note: Consult the default IP ranges table for the defaults used in each region
https://cloud.google.com/composer/docs/composer-2/configure-private-ip#step_1_check_network_requirements
We defined the ranges earlier, in the variables section.<br>

```

### 8.1. Create subnet with the first secondary IP range - for composer pods
Note 1: The command to add both secondary ranges in one shot did not work, hence the two step process<br>
Note 2: Secondary IP range names should be exactly as described below as of 01/13/2022<br>

```
gcloud compute networks subnets create $SHARED_VPC_CC2_SNET_NM \
 --network $SHARED_VPC_NETWORK_NM \
 --range $SHARED_VPC_CC2_SNET_CIDR_BLK \
 --region $PROJECT_LOCATION \
 --enable-private-ip-google-access \
 --project $SHARED_VPC_HOST_PROJECT_ID 
```

### 8.2. Update subnet to add a second  secondary IP range - for composer pods
As of the authoring of this guide (Jan 14, 2022), the secondary IP range name had to strictly be composer-pods
```
 gcloud compute networks subnets update $SHARED_VPC_CC2_SNET_NM \
 --region $PROJECT_LOCATION \
 --add-secondary-ranges composer-pods=$CC2_PODS_CIDR_BLK
```

### 8.3. Update subnet to add asecond  secondary IP range - for composer services
As of the authoring of this guide (Jan 14, 2022), the secondary IP range name had to strictly be composer-services
```
 gcloud compute networks subnets update $SHARED_VPC_CC2_SNET_NM \
 --region $PROJECT_LOCATION \
 --add-secondary-ranges composer-services=$CC2_SVCS_CIDR_BLK
```

### 8.4 Other secondary IP ranges
The other secondary IP ranges listed in the variables should not be created, but reserved for Cloud Composer 2 secure deployment lab module and will be used at Cloud Composer 2 environment provisioning time.


## 9. Create subnets for secure Cloud Dataflow



## 10. Create subnets for secure Cloud Dataproc

## 11. Create subnets for secure Cloud Data Fusion

## 19. Apply organizational policies for the shared VPC host project

Ensure you are authorized to apply organization policies - have the org polict admin role.

```
cat > restrictVpcPeering.yaml << ENDOFFILE
name: projects/$SHARED_VPC_HOST_PROJECT_ID/policies/compute.restrictVpcPeering
spec:
  rules:
  - allowAll: true
ENDOFFILE

gcloud org-policies set-policy restrictVpcPeering.yaml

rm restrictVpcPeering.yaml
```

## 20. Create firewall rules


#### 1. Allow egress from GKE Node IP range to any destination (0.0.0.0/0), TCP/UDP port 53
```
# From Cloud Composer 2 docs
gcloud compute firewall-rules create allow-snet-egress-to-any \
    --network $SHARED_VPC_NETWORK_NM \
    --action allow \
    --direction egress \
    --rules tcp:53,udp:53 \
    --destination-ranges 0.0.0.0/0 \
    --priority 1000 
```

#### 2. Allow egress from GKE Node IP range to GKE Node IP range, all ports
```
# From Cloud Composer 2 docs
gcloud compute firewall-rules create allow-intra-gke-cluster-egress \
    --network $SHARED_VPC_NETWORK_NM \
    --action allow \
    --direction egress \
    --rules ALL \
    --destination-ranges $SHARED_VPC_CC2_SNET_CIDR_BLK \
    --priority 1000 
```

#### 3. Allow egress from GKE Node IP range to GKE Pods IP range, all ports
```
# Applicable for Cloud Composer 2 
gcloud compute firewall-rules create allow-to-gke-pod-sipr-egress \
    --network $SHARED_VPC_NETWORK_NM \
    --action allow \
    --direction egress \
    --rules ALL \
    --destination-ranges $R1_PODS_CIDR_BLK \
    --priority 1000 
```

#### 4. Allow egress from GKE Node IP range to GKE Control Plane IP range, all ports
```
# Applicable for Cloud Composer 2 
gcloud compute firewall-rules create allow-to-gke-ctrl-pln-sipr-egress \
    --network $SHARED_VPC_NETWORK_NM \
    --action allow \
    --direction egress \
    --rules ALL \
    --destination-ranges $R3_GKE_CNTRL_PLN_CIDR_BLK \
    --priority 1000 
```

#### 5. Allow ingress from GCP Health Checks 130.211.0.0/22, 35.191.0.0/16 to GKE Node IP range, TCP ports 80 and 443.
```
# Applicable for Cloud Composer 2 
gcloud compute firewall-rules create allow-gcp-health-chk-ingress \
    --network $SHARED_VPC_NETWORK_NM \
    --action allow \
    --direction ingress \
    --source-ranges 130.211.0.0/22,35.191.0.0/16 \
    --rules tcp:80,tcp:443 \
    --priority 1000 
```

#### 6. Allow egress from GKE Node IP range to GCP Health Checks 130.211.0.0/22, 35.191.0.0/16, TCP ports 80 and 443.
```
# Applicable for Cloud Composer 2 
gcloud compute firewall-rules create allow-to-gcp-health-chk-egress \
    --network $SHARED_VPC_NETWORK_NM \
    --action allow \
    --direction egress \
    --destination-ranges 130.211.0.0/22,35.191.0.0/16 \
    --rules tcp:80,tcp:443 \
    --priority 1000 
```

#### 7. Allow egress from GKE Node IP range to Cloud Composer network IP range, TCP ports 3306 and 3307.
```
# Applicable for Cloud Composer 2 
gcloud compute firewall-rules create allow-to-cc2-sipr-egress \
    --network $SHARED_VPC_NETWORK_NM \
    --action allow \
    --direction egress \
    --destination-ranges $R4_COMPOSER_NET_CIDR_BLK \
    --rules tcp:3306,tcp:3307 \
    --priority 1000 
```

## 21. In host project, IAM permissions for service project's (e2e-demo-indra) service accounts

This is applicable to Cloud Composer 2, potentially other GCP data services as well.

#### 0. Create Composer Agent Service Account in "Shared VPC" project


In the host project, **if this is the first Cloud Composer environment**, then provision the Composer Agent Service Account 
```
gcloud beta services identity create --service=composer.googleapis.com
```


#### 1. Variables

```
DA_PROJECT_GKE_GMSA=service-$DA_PROJECT_NUMBER@container-engine-robot.iam.gserviceaccount.com
DA_PROJECT_CC2_GMSA=service-$DA_PROJECT_NUMBER@cloudcomposer-accounts.iam.gserviceaccount.com
DA_GOOGLE_API_GMSA=$DA_PROJECT_NUMBER@cloudservices.gserviceaccount.com
```

#### 2. GKE default service account specific

a) Compute Network User role
```
gcloud projects add-iam-policy-binding ${SHARED_VPC_HOST_PROJECT_ID} \
    --member=serviceAccount:${DA_PROJECT_GKE_GMSA} \
    --role=roles/compute.networkUser 
```

b) Container Host Service Agent User role
```
gcloud projects add-iam-policy-binding ${SHARED_VPC_HOST_PROJECT_ID} \
    --member=serviceAccount:${DA_PROJECT_GKE_GMSA} \
    --role roles/container.hostServiceAgentUser
```

#### 3. Cloud Composer 2 default service account specific

a) Compute Network User role
```
gcloud projects add-iam-policy-binding ${SHARED_VPC_HOST_PROJECT_ID} \
    --member=serviceAccount:${DA_PROJECT_CC2_GMSA} \
        --role=roles/compute.networkUser 
```  

b) Composer Shared VPC Agent role
```
gcloud projects add-iam-policy-binding ${SHARED_VPC_HOST_PROJECT_ID} \
    --member=serviceAccount:${DA_PROJECT_CC2_GMSA} \
        --role=roles/composer.sharedVpcAgent 
```  
 
#### 4. Google APIs default service account specific

```      
gcloud projects add-iam-policy-binding ${SHARED_VPC_HOST_PROJECT_ID} \
    --member=serviceAccount:${DA_GOOGLE_API_GMSA} \
        --role=roles/compute.networkUser 
```

#### 5. User managed service account specific
```
gcloud projects add-iam-policy-binding ${SHARED_VPC_HOST_PROJECT_ID} \
    --member=serviceAccount:${DA_PROJECT_UMSA_FQN} \
    --role=roles/compute.networkUser 
```

#### 6. Google Managed Cloud Dataflow service account specific
```
CDF_GMSA=service-$DA_PROJECT_NUMBER@dataflow-service-producer-prod.iam.gserviceaccount.com

gcloud projects add-iam-policy-binding ${SHARED_VPC_HOST_PROJECT_ID} \
    --member=serviceAccount:${CDF_GMSA} \
    --role=roles/compute.networkUser 
```

## 22. DNS configuration

This is applicable to Cloud Composer 2, potentially other GCP data services as well.


#### 1. Create DNS zone
```
gcloud beta dns --project=e2e-demo-indra-shared managed-zones create pkg-dev --description="" --dns-name="pkg.dev." --visibility="private" --networks="indra-vpc-shared"
```

#### 2. Create CNAME records
```
gcloud beta dns --project=e2e-demo-indra-shared record-sets transaction start --zone="pkg-dev" 

gcloud beta dns --project=e2e-demo-indra-shared record-sets transaction add pkg.dev. --name="*.pkg.dev." --ttl="300" --type="CNAME" --zone="pkg-dev" 

gcloud beta dns --project=e2e-demo-indra-shared record-sets transaction execute --zone="pkg-dev"
```

#### 3. Create A records
```
gcloud beta dns --project=e2e-demo-indra-shared record-sets transaction start --zone="pkg-dev" 

gcloud beta dns --project=e2e-demo-indra-shared record-sets transaction add 199.36.153.4 199.36.153.5 199.36.153.6 199.36.153.7 --name="pkg.dev." --ttl="300" --type="A" --zone="pkg-dev" 

gcloud beta dns --project=e2e-demo-indra-shared record-sets transaction execute --zone="pkg-dev"

```



## 23. Create Cloud Router for pypi/maven etc access from VPC

Docs: https://cloud.google.com/network-connectivity/docs/router/how-to/creating-routers

```
gcloud compute routers create indra-router-shared \
    --project=$SHARED_VPC_HOST_PROJECT_ID \
    --network=$SHARED_VPC_NETWORK_NM \
    --asn=65000 \
    --region=$LOCATION
```

## 24. Create Cloud NAT for for pypi/maven etc access from VPC

Docs: https://cloud.google.com/nat/docs/gke-example#create-nat

```
gcloud compute routers nats create indra-nat-shared \
    --router=indra-router-shared \
    --auto-allocate-nat-external-ips \
    --nat-all-subnet-ip-ranges \
    --enable-logging \
    --region=$LOCATION
```

# 25. Create a VPC-SC

In your host project, enable the following Google APIs-
```
gcloud services enable cloudsql.googleapis.com
gcloud services enable bigquery.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable pubsub.googleapis.com
# Add GKE, GCE, ...
```
