# About

This module covers creation of a Shared VPC, subnets, requisite organizational policies, associated firewall rules, associated IAM permissions, in preparation of a secure and realistic Cloud Composer setup.<br>

Shared VPC enables organizations to establish budgeting and access control boundaries at the project level while allowing for secure and efficient communication using private IPs across those boundaries. In the Shared VPC configuration, Cloud Composer can invoke services hosted in other Google Cloud projects in the same organization without exposing services to the public internet.

<br>
Shared VPC requires that you designate a host project to which networks and subnetworks belong and a service project, which is attached to the host project. When Cloud Composer participates in a Shared VPC, the Cloud Composer environment is in the service project.<br><br>

To set up Shared VPC, you will need to pre-define the following IP ranges in the host project:

- Primary IP Range of the subnet used by GKE nodes that Cloud Composer uses as its Compute Engine layer.
- Secondary IP Range for GKE services.
- Secondary IP Range for GKE pods.
- Secondary IP Ranges cannot overlap with any other secondary ranges in this VPC.
And ensure that secondary ranges are large enough to accommodate the cluster's size and your environment scaling.<br><br>

[References](https://cloud.google.com/composer/docs/composer-2/configure-shared-vpc)
<hr>

**Dependencies**<br>
Successful completion of Module 2.

## 1. Create a project for "Shared VPC" called e2e-demo-indra-shared

Create a new project for the shared VPC.


## 2. Variables for use in the sub-module

In cloud shell scoped to the shared VPC/host project, paste the following variables after **updating the same to match your environment**-
```
ORG_ID=akhanolkar.altostrat.com #Replace with yours
ORG_ID_NBR=236589261571 #Replace with yours

DA_PROJECT_NUMBER=914583619622
DA_PROJECT_ID=e2e-demo-indra #Data analytics project

SHARED_VPC_HOST_PROJECT_ID=$DA_PROJECT_ID-shared #Shared VPC project

PROJECT_LOCATION=us-central1
LOCATION=us-central1

ADMIN_UPN_FQN=admin@$ORG_ID #Replace with yours if its a different construct
DA_PROJECT_UMSA="indra-sa"
DA_PROJECT_UMSA_FQN=$DA_PROJECT_UMSA@$DA_PROJECT_ID.iam.gserviceaccount.com

SHARED_VPC_NETWORK_NM=indra-vpc-shared
SHARED_VPC_FQN="projects/$SHARED_VPC_HOST_PROJECT_ID/global/networks/$SHARED_VPC_NETWORK_NM"
SHARED_VPC_CC2_SNET_NM="indra-composer2-snet-shared"
SHARED_VPC_CC2_SNET_FQN="projects/$SHARED_VPC_HOST_PROJECT_ID/regions/$PROJECT_LOCATION/subnetworks/$SHARED_VPC_CC2_SNET_NM"

SHARED_VPC_CC2_SNET_CIDR_BLK='10.65.61.0/24' # Number of GKE nodes and ILBs available 
CC2_PODS_CIDR_BLK='10.66.0.0/16' # Composer pods, ensure sufficient, especially for autoscale
CC2_SVCS_CIDR_BLK='10.67.0.0/16' # Composer pods, ensure sufficient, especially for autoscale
GKE_CNTRL_PLN_CIDR_BLK='10.65.62.0/24' 
CC2_CIDR_BLK='10.65.63.0/24' 
CSQL_CIDR_BLK='10.65.64.0/24'

```
## 3. Enable Google APIs in the shared VPC host project

In cloud shell scoped to the shared VPC/host project, run the commands below-

```
gcloud services enable container.googleapis.com --project $SHARED_VPC_HOST_PROJECT_ID
gcloud services enable orgpolicy.googleapis.com --project $SHARED_VPC_HOST_PROJECT_ID
```

## 4. Grant IAM role to the admininstrator (or yourself), to create a "Shared VPC"

In cloud shell scoped to the shared VPC/host project, run the below:
```
gcloud organizations add-iam-policy-binding $ORG_ID_NBR \
  --member=user:$ADMIN_UPN_FQN \
  --role="roles/compute.xpnAdmin"
```

## 5. Enable shared VPC for the "Shared VPC" project

In cloud shell scoped to the shared VPC/host project, run the below:
```
gcloud compute shared-vpc enable $SHARED_VPC_HOST_PROJECT_ID
```

## 6. Associate your data analytics project with the "Shared VPC" project

In cloud shell scoped to the shared VPC/host project, run the below:
```
gcloud compute shared-vpc associated-projects add $DA_PROJECT_ID \
    --host-project $SHARED_VPC_HOST_PROJECT_ID
```

## 7. Review IP range considerations for Cloud Composer 2

A core requirement here is to ensure there is no CIDR range overlap between your ranges and the Google services
<br>Review the documentation [here](
https://cloud.google.com/composer/docs/composer-2/configure-private-ip#step_1_check_network_requirements)


## 8. Create a VPC in the "shared VPC" project

In cloud shell scoped to the shared VPC/host project, run the below:
```
gcloud compute networks create $SHARED_VPC_NETWORK_NM \
--project=$SHARED_VPC_HOST_PROJECT_ID \
--subnet-mode=custom \
--mtu=1460 \
--bgp-routing-mode=regional
```

## 9. Create subnet for secure Cloud Composer 2

Per the docs as of Jan 25, 2022, these are considerations-
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

### 9.1. Create subnet with the first secondary IP range - for composer pods

In cloud shell scoped to the shared VPC/host project, run the below:
```
gcloud compute networks subnets create $SHARED_VPC_CC2_SNET_NM \
 --network $SHARED_VPC_NETWORK_NM \
 --range $SHARED_VPC_CC2_SNET_CIDR_BLK \
 --region $PROJECT_LOCATION \
 --enable-private-ip-google-access \
 --project $SHARED_VPC_HOST_PROJECT_ID 
```

### 9.2. Update subnet to add a second  secondary IP range - for composer pods
*As of the authoring of this guide (Jan 14, 2022), the secondary IP range name had to strictly be composer-pods.*<br>
In cloud shell scoped to the shared VPC/host project, run the below:
```
 gcloud compute networks subnets update $SHARED_VPC_CC2_SNET_NM \
 --region $PROJECT_LOCATION \
 --add-secondary-ranges composer-pods=$CC2_PODS_CIDR_BLK
```

### 9.3. Update subnet to add asecond  secondary IP range - for composer services
*As of the authoring of this guide (Jan 14, 2022), the secondary IP range name had to strictly be composer-services*<br>
In cloud shell scoped to the shared VPC/host project, run the below:
```
 gcloud compute networks subnets update $SHARED_VPC_CC2_SNET_NM \
 --region $PROJECT_LOCATION \
 --add-secondary-ranges composer-services=$CC2_SVCS_CIDR_BLK
```

### 9.4 Other secondary IP ranges
The other secondary IP ranges listed in the variables should not be created, but **reserved** for Cloud Composer 2 secure deployment lab sub-module and will be used at environment provisioning time.



## 10. Apply organizational policies for the shared VPC host project

*Ensure you are authorized to apply organization policies - have the org policy admin role.*<br>

In cloud shell scoped to the shared VPC/host project, run the below:
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

## 11. Create firewall rules


#### 11.1. Allow egress from GKE Node IP range to any destination (0.0.0.0/0), TCP/UDP port 53

In cloud shell scoped to the shared VPC/host project, run the below:
```
gcloud compute firewall-rules create allow-snet-egress-to-any \
    --network $SHARED_VPC_NETWORK_NM \
    --action allow \
    --direction egress \
    --rules tcp:53,udp:53 \
    --destination-ranges 0.0.0.0/0 \
    --priority 1000 
```

#### 11.2. Allow egress from GKE Node IP range to GKE Node IP range, all ports

In cloud shell scoped to the shared VPC/host project, run the below:
```
gcloud compute firewall-rules create allow-intra-gke-cluster-egress \
    --network $SHARED_VPC_NETWORK_NM \
    --action allow \
    --direction egress \
    --rules ALL \
    --destination-ranges $SHARED_VPC_CC2_SNET_CIDR_BLK \
    --priority 1000 
```

#### 11.3. Allow egress from GKE Node IP range to GKE Pods IP range, all ports

In cloud shell scoped to the shared VPC/host project, run the below:
```
gcloud compute firewall-rules create allow-to-gke-pod-sipr-egress \
    --network $SHARED_VPC_NETWORK_NM \
    --action allow \
    --direction egress \
    --rules ALL \
    --destination-ranges $R1_PODS_CIDR_BLK \
    --priority 1000 
```

#### 11.4. Allow egress from GKE Node IP range to GKE Control Plane IP range, all ports

In cloud shell scoped to the shared VPC/host project, run the below:
```
gcloud compute firewall-rules create allow-to-gke-ctrl-pln-sipr-egress \
    --network $SHARED_VPC_NETWORK_NM \
    --action allow \
    --direction egress \
    --rules ALL \
    --destination-ranges $R3_GKE_CNTRL_PLN_CIDR_BLK \
    --priority 1000 
```

#### 11.5. Allow ingress from GCP Health Checks 130.211.0.0/22, 35.191.0.0/16 to GKE Node IP range, TCP ports 80 and 443.

In cloud shell scoped to the shared VPC/host project, run the below:
```
gcloud compute firewall-rules create allow-gcp-health-chk-ingress \
    --network $SHARED_VPC_NETWORK_NM \
    --action allow \
    --direction ingress \
    --source-ranges 130.211.0.0/22,35.191.0.0/16 \
    --rules tcp:80,tcp:443 \
    --priority 1000 
```

#### 11.6. Allow egress from GKE Node IP range to GCP Health Checks 130.211.0.0/22, 35.191.0.0/16, TCP ports 80 and 443.

In cloud shell scoped to the shared VPC/host project, run the below:
```
gcloud compute firewall-rules create allow-to-gcp-health-chk-egress \
    --network $SHARED_VPC_NETWORK_NM \
    --action allow \
    --direction egress \
    --destination-ranges 130.211.0.0/22,35.191.0.0/16 \
    --rules tcp:80,tcp:443 \
    --priority 1000 
```

#### 11.7. Allow egress from GKE Node IP range to Cloud Composer network IP range, TCP ports 3306 and 3307.

In cloud shell scoped to the shared VPC/host project, run the below:
```
gcloud compute firewall-rules create allow-to-cc2-sipr-egress \
    --network $SHARED_VPC_NETWORK_NM \
    --action allow \
    --direction egress \
    --destination-ranges $R4_COMPOSER_NET_CIDR_BLK \
    --rules tcp:3306,tcp:3307 \
    --priority 1000 
```

## 12. In host project, IAM permissions for service project's (e2e-demo-indra) service accounts


#### 12.1. Create Composer Agent Service Account in "Shared VPC" project


In the host project, **if this is the first Cloud Composer environment**, provision the Composer Agent Service Account 

```
gcloud beta services identity create --service=composer.googleapis.com
```


#### 12.2. IAM permissions related variables

In cloud shell scoped to the shared VPC/host project, run the below. <br>Each of these maps to a service account in the service project:
```
DA_PROJECT_GKE_GMSA=service-$DA_PROJECT_NUMBER@container-engine-robot.iam.gserviceaccount.com
DA_PROJECT_CC2_GMSA=service-$DA_PROJECT_NUMBER@cloudcomposer-accounts.iam.gserviceaccount.com
DA_GOOGLE_API_GMSA=$DA_PROJECT_NUMBER@cloudservices.gserviceaccount.com
```

#### 12.3. Apply GKE default service account specific IAM permissions

In cloud shell scoped to the shared VPC/host project, run the below.<br>

##### 12.3.1. Compute Network User role
```
gcloud projects add-iam-policy-binding ${SHARED_VPC_HOST_PROJECT_ID} \
    --member=serviceAccount:${DA_PROJECT_GKE_GMSA} \
    --role=roles/compute.networkUser 
```

##### 12.3.2. Container Host Service Agent User role
```
gcloud projects add-iam-policy-binding ${SHARED_VPC_HOST_PROJECT_ID} \
    --member=serviceAccount:${DA_PROJECT_GKE_GMSA} \
    --role roles/container.hostServiceAgentUser
```

#### 12.4. Cloud Composer 2 default service account specific

In cloud shell scoped to the shared VPC/host project, run the below.<br>

##### 12.4.1. Compute Network User role
```
gcloud projects add-iam-policy-binding ${SHARED_VPC_HOST_PROJECT_ID} \
    --member=serviceAccount:${DA_PROJECT_CC2_GMSA} \
        --role=roles/compute.networkUser 
```  

##### 12.4.2. Composer Shared VPC Agent role
```
gcloud projects add-iam-policy-binding ${SHARED_VPC_HOST_PROJECT_ID} \
    --member=serviceAccount:${DA_PROJECT_CC2_GMSA} \
        --role=roles/composer.sharedVpcAgent 
```  
 
#### 12.5. Google APIs default service account specific
In cloud shell scoped to the shared VPC/host project, run the below.<br>

```      
gcloud projects add-iam-policy-binding ${SHARED_VPC_HOST_PROJECT_ID} \
    --member=serviceAccount:${DA_GOOGLE_API_GMSA} \
        --role=roles/compute.networkUser 
```

#### 12.6. User managed service account specific

In cloud shell scoped to the shared VPC/host project, run the below.<br>
```
gcloud projects add-iam-policy-binding ${SHARED_VPC_HOST_PROJECT_ID} \
    --member=serviceAccount:${DA_PROJECT_UMSA_FQN} \
    --role=roles/compute.networkUser 
```

#### 12.7. Google Managed Cloud Dataflow service account specific


In cloud shell scoped to the shared VPC/host project, run the below.<br>
```
CDF_GMSA=service-$DA_PROJECT_NUMBER@dataflow-service-producer-prod.iam.gserviceaccount.com

gcloud projects add-iam-policy-binding ${SHARED_VPC_HOST_PROJECT_ID} \
    --member=serviceAccount:${CDF_GMSA} \
    --role=roles/compute.networkUser 
```


