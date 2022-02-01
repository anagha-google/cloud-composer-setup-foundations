# About

This module covers configuring VPC-SC and PSC over and above the secure setup from the prior secure setup module.
<br>

The following are the variabes we will use, execute the same in cloud shell scoped to your host project-
```
ORG_ID=akhanolkar.altostrat.com #Replace with yours
ORG_ID_NUMBER=236589261571 #Replace with yours

SVC_PROJECT_NUMBER=187732393981 #Replace with yours
SVC_PROJECT_ID=zeus-svc-proj #Data analytics service project

SHARED_VPC_HOST_PROJECT_ID=zeus-host-proj        #Shared VPC project - replace with yours
SHARED_VPC_HOST_PROJECT_NUMBER=322087561681        #Shared VPC project - replace with yours


LOCATION=us-central1

ADMIN_UPN_FQN=admin@$ORG_ID #Replace with yours if its a different construct
SVC_PROJECT_UMSA="zeus-sa"
SVC_PROJECT_UMSA_FQN=$SVC_PROJECT_UMSA@$SVC_PROJECT_ID.iam.gserviceaccount.com

SHARED_VPC_NETWORK_NM=zeus-shared-vpc
SHARED_VPC_FQN="projects/$SHARED_VPC_HOST_PROJECT_ID/global/networks/$SHARED_VPC_NETWORK_NM"
SHARED_VPC_CC2_SNET_NM="zeus-shared-cc2-snet"
SHARED_VPC_CC2_SNET_FQN="projects/$SHARED_VPC_HOST_PROJECT_ID/regions/$LOCATION/subnetworks/$SHARED_VPC_CC2_SNET_NM"

SHARED_VPC_CONNECTOR_SNET_NM=zeus-vpc-cnctr-snet

SHARED_VPC_CC2_SNET_CIDR_BLK='10.65.61.0/24' # Number of GKE nodes and ILBs available 

OFFICE_CIDR=98.222.97.10/32 # Replace with your CIDR
```

## 1. Enable APIs in both service and host projects

```
gcloud services enable accesscontextmanager.googleapis.com
```

## 2. IAM permissions to operate with Access Context Manager in host project

```
gcloud organizations add-iam-policy-binding $ORG_ID_NUMBER \
    --member="user:$ADMIN_UPN_FQN" \
    --role="roles/accesscontextmanager.policyAdmin"
```

### 3. Create Access Context Manager in host project

If you dont have a default polciy, create one- 
```
gcloud access-context-manager policies create \
--organization $ORG_ID_NUMBER --title Zeus_CC2_Access_Policy
```

Grab its identifier -
```
ACM_POLICY_NUMBER=`gcloud access-context-manager policies list --organization $ORG_ID_NUMBER | grep NAME | cut -d':' -f2 | sed 's/^ *//g'`
```
