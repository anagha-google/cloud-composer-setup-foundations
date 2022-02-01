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

## 3. Create Access Context Manager policy in host project

a) If you dont have a default policy in your organization, create one- 
```
gcloud access-context-manager policies create \
--organization $ORG_ID_NUMBER --title Zeus_CC2_Access_Policy
```

b) Grab its identifier -
```
ACM_POLICY_NUMBER=`gcloud access-context-manager policies list --organization $ORG_ID_NUMBER | grep NAME | cut -d':' -f2 | sed 's/^ *//g'`
```

## 4. Create an access level for the operator and the Cloud Build GMSA in the host project

Both the UPN and the service project Cloud Build Google Managed Service Account will need access to the perimeter. Configure the same.

```
SVC_PROJECT_CLOUD_BUILD_GMSA_FQN=$SVC_PROJECT_NUMBER@cloudbuild.gserviceaccount.com

cat > access_conditions.yaml << ENDOFFILE
- members:
    - user:$ADMIN_UPN_FQN
    - serviceAccount:$SVC_PROJECT_CLOUD_BUILD_GMSA_FQN
ENDOFFILE
```

```
gcloud access-context-manager levels create UPN_SPN_ACCESS_LVL \
   --title UPN_SPN_ACCESS_LVL \
   --basic-level-spec access_conditions.yaml \
   --combine-function=OR \
   --policy=$ACM_POLICY_NUMBER
```

## 5. Create a VPC-SC perimeter around an existing set of services 



## 6. Create DNS entries from the host project 

https://cloud.google.com/composer/docs/composer-2/configure-vpc-sc#connectivity_to_the_restrictedgoogleapiscom_endpoint
```
Configure connectivity to the restricted.googleapis.com endpoint:

Verify the existence of a DNS mapping from *.googleapis.com to restricted.googleapis.com.

DNS *.gcr.io should resolve to 199.36.153.4/30 similarly to the googleapis.com endpoint. To do that, create a new zone as: CNAME *.gcr.io -> gcr.io. A gcr.io. -> 199.36.153.4, 199.36.153.5, 199.36.153.6, 199.36.153.7.

DNS *.pkg.dev should resolve to 199.36.153.4/30 similarly to the googleapis.com endpoint. To do that, create a new zone as: CNAME *.pkg.dev -> pkg.dev. A pkg.dev. -> 199.36.153.4, 199.36.153.5, 199.36.153.6, 199.36.153.7.

DNS *.composer.cloud.google.com should resolve to 199.36.153.4/30 similarly to the googleapis.com endpoint. To do that, create a new zone as: CNAME *.composer.cloud.google.com -> composer.cloud.google.com. A composer.cloud.google.com. -> 199.36.153.4, 199.36.153.5, 199.36.153.6, 199.36.153.7.
```


### 6.1. DNS entries googleapis.com
#### 6.1.a Create zone

```
gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID managed-zones create googleapis --description="" \
--dns-name="googleapis.com." \
--visibility="private" \
--networks=$SHARED_VPC_NETWORK_NM
gcloud beta dns --project=e2e-demo-indra-shared \
record-sets transaction start --zone="googleapis" 
```

#### 6.1.b Create A record

```
gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID record-sets transaction start --zone="googleapis" && gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID \
record-sets transaction add 199.36.153.4 199.36.153.5 199.36.153.6 199.36.153.7 --name="restricted.googleapis.com." --ttl="300" --type="A" --zone="googleapis" && && gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID record-sets transaction execute --zone="googleapis"

```

#### 6.1.c Create CNAME record

```
gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID record-sets transaction start --zone="googleapis" && gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID record-sets transaction add restricted.googleapis.com. --name="*.googleapis.com." --ttl="300" --type="CNAME" --zone="googleapis" && gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID record-sets transaction execute --zone="googleapis"

```


### 6.2. DNS entries gcr.io
#### 6.2.a Create zone

```
gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID managed-zones create gcr-io --description="" \
--dns-name="gcr.io." \
--visibility="private" \
--networks=$SHARED_VPC_NETWORK_NM
```

#### 6.2.b Create A record

```
gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID record-sets transaction start --zone="gcr-io" && gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID record-sets transaction add 199.36.153.4 199.36.153.5 199.36.153.6 199.36.153.7 --name="gcr.io." --ttl="300" --type="A" --zone="gcr-io" && gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID record-sets transaction execute --zone="gcr-io"
```

#### 6.2.c Create CNAME record

```
gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID record-sets transaction start --zone="gcr-io" && gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID record-sets transaction add gcr.io. --name="*.gcr.io." --ttl="300" --type="CNAME" --zone="gcr-io" && gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID record-sets transaction execute --zone="gcr-io"

```

### 6.3. DNS entries composer.cloud.google.com
#### 6.3.a Create zone

```
gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID managed-zones create composer-cloud-google --description="" --dns-name="composer.cloud.google.com." --visibility="private" --networks=$SHARED_VPC_NETWORK_NM
```

#### 6.3.b Create A record

```
gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID record-sets transaction start --zone="composer-cloud-google" && gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID record-sets transaction add 199.36.153.4 199.36.153.5 199.36.153.6 199.36.153.7 --name="composer.cloud.google.com." --ttl="300" --type="A" --zone="composer-cloud-google" && gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID record-sets transaction execute --zone="composer-cloud-google"
```

#### 6.3.c Create CNAME record

```
gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID record-sets transaction start --zone="composer-cloud-google" && gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID record-sets transaction add composer.cloud.google.com. --name="*.composer.cloud.google.com." --ttl="300" --type="CNAME" --zone="composer-cloud-google" && gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID record-sets transaction execute --zone="composer-cloud-google"

```