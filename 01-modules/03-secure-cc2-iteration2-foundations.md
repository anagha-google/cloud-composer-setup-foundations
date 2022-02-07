# About

This module covers configuring VPC-SC over and above the secure setup from the prior secure setup module.
<br>

The following are the variabes we will use, execute the same in cloud shell scoped to your host project-
```

# Replace with your keyword from module 1
PROJECT_KEYWORD="thor"  

#Replace with yours
OFFICE_CIDR=98.222.97.10/32 

ORG_ID=akhanolkar.altostrat.com                              
ORG_ID_NUMBER=236589261571                                      

SVC_PROJECT_NUMBER=509862753528                              
SVC_PROJECT_ID=$PROJECT_KEYWORD-svc-proj                     

SHARED_VPC_HOST_PROJECT_ID=$PROJECT_KEYWORD-host-proj        
SHARED_VPC_HOST_PROJECT_NUMBER=239457183145                  

ADMIN_UPN_FQN=admin@$ORG_ID 

SVC_PROJECT_UMSA="$PROJECT_KEYWORD-sa"
SVC_PROJECT_UMSA_FQN=$SVC_PROJECT_UMSA@$SVC_PROJECT_ID.iam.gserviceaccount.com

COMPOSER_ENV_NM=cc2-$PROJECT_KEYWORD-secure
LOCATION=us-central1

SHARED_VPC_NETWORK_NM=$PROJECT_KEYWORD-shared-vpc
SHARED_VPC_FQN="projects/$SHARED_VPC_HOST_PROJECT_ID/global/networks/$SHARED_VPC_NETWORK_NM"
SHARED_VPC_CC2_SNET_NM="$PROJECT_KEYWORD-shared-cc2-snet"
SHARED_VPC_CC2_SNET_FQN="projects/$SHARED_VPC_HOST_PROJECT_ID/regions/$LOCATION/subnetworks/$SHARED_VPC_CC2_SNET_NM"

SHARED_VPC_CONNECTOR_SNET_NM=$PROJECT_KEYWORD-vpc-cnctr-snet
SHARED_VPC_CONNECTOR_SNET_CIDR=10.70.0.0/28


VPC_SC_SERVICES_SCOPE="bigquery.googleapis.com,dataflow.googleapis.com,cloudfunctions.googleapis.com,pubsub.googleapis.com,sqladmin.googleapis.com,storage.googleapis.com,compute.googleapis.com,container.googleapis.com,containerregistry.googleapis.com,monitoring.googleapis.com,composer.googleapis.com,artifactregistry.googleapis.com"
```

## 1. Enable APIs in both service and host projects

```
gcloud services enable accesscontextmanager.googleapis.com
gcloud services enable cloudresourcemanager.googleapis.com
gcloud services enable vpcaccess.googleapis.com 
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
--organization $ORG_ID_NUMBER --title $PROJECT_KEYWORD_CC2_access_policy
```

b) Grab its identifier -
```
ACM_POLICY_NUMBER=`gcloud access-context-manager policies list --organization $ORG_ID_NUMBER | grep NAME | cut -d':' -f2 | sed 's/^ *//g'`
```

## 4. Create access levels in the host project for the VPC perimeter 

### 4.1. Create access level for the office CIDR & VPC Access Connector Subnet

```
cat > ip_access_conditions.yaml << ENDOFFILE
- ipSubnetworks:
  - $OFFICE_CIDR
ENDOFFILE
```

```
gcloud access-context-manager levels create OFFICE_CIDR_ACCESS_LVL \
   --title OFFICE_CIDR_ACCESS_LVL \
   --basic-level-spec ip_access_conditions.yaml \
   --combine-function=OR \
   --policy=$ACM_POLICY_NUMBER
```

Delete the file once the access level is created-
```
rm ip_access_conditions.yaml
```

### 4.2. Create access level for the operator and the Cloud Build GMSA 

Both the UPN and the service project Cloud Build Google Managed Service Account will need access to the perimeter. Configure the same.


```
rm access_conditions.yaml

SVC_PROJECT_CLOUD_BUILD_GMSA_FQN=$SVC_PROJECT_NUMBER@cloudbuild.gserviceaccount.com
SVC_PROJECT_CLOUD_FUNCTION_GMSA_FQN=service-$SVC_PROJECT_NUMBER@gcf-admin-robot.iam.gserviceaccount.com

cat > access_conditions.yaml << ENDOFFILE
- members:
    - user:$ADMIN_UPN_FQN
    - serviceAccount:$SVC_PROJECT_CLOUD_BUILD_GMSA_FQN
    - serviceAccount:$SVC_PROJECT_CLOUD_FUNCTION_GMSA_FQN
    - serviceAccount:$SVC_PROJECT_UMSA_FQN
ENDOFFILE
```

```
gcloud access-context-manager levels create UPN_SPN_ACCESS_LVL \
   --title UPN_SPN_ACCESS_LVL \
   --basic-level-spec access_conditions.yaml \
   --combine-function=OR \
   --policy=$ACM_POLICY_NUMBER
```


Delete the file once the access level is created-
```
rm access_conditions.yaml
```

## 5. Create DNS entries in the host project for googleapis.com, gcr.io and composer.cloud.google.com

https://cloud.google.com/composer/docs/composer-2/configure-vpc-sc#connectivity_to_the_restrictedgoogleapiscom_endpoint
```
Configure connectivity to the restricted.googleapis.com endpoint:

Verify the existence of a DNS mapping from *.googleapis.com to restricted.googleapis.com.

DNS *.gcr.io should resolve to 199.36.153.4/30 similarly to the googleapis.com endpoint. To do that, create a new zone as: CNAME *.gcr.io -> gcr.io. A gcr.io. -> 199.36.153.4, 199.36.153.5, 199.36.153.6, 199.36.153.7.

DNS *.pkg.dev should resolve to 199.36.153.4/30 similarly to the googleapis.com endpoint. To do that, create a new zone as: CNAME *.pkg.dev -> pkg.dev. A pkg.dev. -> 199.36.153.4, 199.36.153.5, 199.36.153.6, 199.36.153.7.

DNS *.composer.cloud.google.com should resolve to 199.36.153.4/30 similarly to the googleapis.com endpoint. To do that, create a new zone as: CNAME *.composer.cloud.google.com -> composer.cloud.google.com. A composer.cloud.google.com. -> 199.36.153.4, 199.36.153.5, 199.36.153.6, 199.36.153.7.
```


### 5.1. DNS entries googleapis.com
#### 5.1.a Create zone

```
gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID managed-zones create googleapis --description="" \
--dns-name="googleapis.com." \
--visibility="private" \
--networks=$SHARED_VPC_NETWORK_NM
```

#### 5.1.b Create A record

```
gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID record-sets transaction start --zone="googleapis" && gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID \
record-sets transaction add 199.36.153.4 199.36.153.5 199.36.153.6 199.36.153.7 --name="restricted.googleapis.com." --ttl="300" --type="A" --zone="googleapis" &&  gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID record-sets transaction execute --zone="googleapis"

```

#### 5.1.c Create CNAME record

```
gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID record-sets transaction start --zone="googleapis" && gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID record-sets transaction add restricted.googleapis.com. --name="*.googleapis.com." --ttl="300" --type="CNAME" --zone="googleapis" && gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID record-sets transaction execute --zone="googleapis"

```


### 5.2. DNS entries gcr.io
#### 5.2.a Create zone

```
gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID managed-zones create gcr-io --description="" \
--dns-name="gcr.io." \
--visibility="private" \
--networks=$SHARED_VPC_NETWORK_NM
```

#### 5.2.b Create A record

```
gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID record-sets transaction start --zone="gcr-io" && gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID record-sets transaction add 199.36.153.4 199.36.153.5 199.36.153.6 199.36.153.7 --name="gcr.io." --ttl="300" --type="A" --zone="gcr-io" && gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID record-sets transaction execute --zone="gcr-io"
```

#### 5.2.c Create CNAME record

```
gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID record-sets transaction start --zone="gcr-io" && gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID record-sets transaction add gcr.io. --name="*.gcr.io." --ttl="300" --type="CNAME" --zone="gcr-io" && gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID record-sets transaction execute --zone="gcr-io"

```

### 5.3. DNS entries composer.cloud.google.com
#### 5.3.a Create zone

```
gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID managed-zones create composer-cloud-google --description="" --dns-name="composer.cloud.google.com." --visibility="private" --networks=$SHARED_VPC_NETWORK_NM
```

#### 5.3.b Create A record

```
gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID record-sets transaction start --zone="composer-cloud-google" && gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID record-sets transaction add 199.36.153.4 199.36.153.5 199.36.153.6 199.36.153.7 --name="composer.cloud.google.com." --ttl="300" --type="A" --zone="composer-cloud-google" && gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID record-sets transaction execute --zone="composer-cloud-google"
```

#### 5.3.c Create CNAME record

```
gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID record-sets transaction start --zone="composer-cloud-google" && gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID record-sets transaction add composer.cloud.google.com. --name="*.composer.cloud.google.com." --ttl="300" --type="CNAME" --zone="composer-cloud-google" && gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID record-sets transaction execute --zone="composer-cloud-google"

```

## 6.0 Configure incremental firewall rules in the host project

To connect to restricted Google APIs..
```
gcloud compute --project=$SHARED_VPC_HOST_PROJECT_ID firewall-rules create allow-gke-egress-rgapis \
--direction=EGRESS \
--priority=1000 \
--network=$SHARED_VPC_NETWORK_NM \
--action=ALLOW \
--rules=tcp:443 \
--destination-ranges=199.36.153.4/30
```

## 7.0. Create the VPC perimeter 

### 7.0.1. Create policies file for ingress 

```
rm $PROJECT_KEYWORD-perimeter-ingress-policies.yaml

cat > $PROJECT_KEYWORD-perimeter-ingress-policies.yaml << ENDOFFILE

  - 
    ingressFrom: 
      identities: 
        - "user:$ADMIN_UPN_FQN"
      sources: 
        - 
          accessLevel: accessPolicies/$ACM_POLICY_NUMBER/accessLevels/UPN_SPN_ACCESS_LVL
        - 
          accessLevel: accessPolicies/$ACM_POLICY_NUMBER/accessLevels/OFFICE_CIDR_ACCESS_LVL
    ingressTo: 
      operations: 
        - 
          serviceName: "*"
      resources: 
        - projects/$SHARED_VPC_HOST_PROJECT_NUMBER
        - projects/$SVC_PROJECT_NUMBER
  - 
    ingressFrom: 
      identities: 
        - "serviceAccount:$SVC_PROJECT_UMSA_FQN"
      sources: 
        - 
          accessLevel: accessPolicies/$ACM_POLICY_NUMBER/accessLevels/UPN_SPN_ACCESS_LVL
        - 
          accessLevel: accessPolicies/$ACM_POLICY_NUMBER/accessLevels/OFFICE_CIDR_ACCESS_LVL
    ingressTo: 
      operations: 
        - 
          serviceName: "*"
      resources: 
        - projects/$SHARED_VPC_HOST_PROJECT_NUMBER
        - projects/$SVC_PROJECT_NUMBER
ENDOFFILE
```

### 7.0.2. Create policies file for egress 

```
rm $PROJECT_KEYWORD-perimeter-egress-policies.yaml

cat > $PROJECT_KEYWORD-perimeter-egress-policies.yaml << ENDOFFILE

  - 
    egressFrom: 
      identityType: ANY_SERVICE_ACCOUNT
    egressTo: 
      operations: 
        - 
          serviceName: "*"
      resources: 
        - projects/$SHARED_VPC_HOST_PROJECT_NUMBER
        - projects/$SVC_PROJECT_NUMBER
  - 
    egressFrom: 
      identities: 
        - "user:$ADMIN_UPN_FQN"
    egressTo: 
      operations: 
        - 
          serviceName: "*"
      resources: 
        - projects/$SHARED_VPC_HOST_PROJECT_NUMBER
        - projects/$SVC_PROJECT_NUMBER

ENDOFFILE
```

### 7.0.3. Create perimeter

```
gcloud access-context-manager perimeters create ${PROJECT_KEYWORD}_perimeter --title=${PROJECT_KEYWORD}_perimeter \
--perimeter-type="regular" \
--resources=projects/$SVC_PROJECT_NUMBER,projects/$SHARED_VPC_HOST_PROJECT_NUMBER \
--access-levels=accessPolicies/$ACM_POLICY_NUMBER/accessLevels/UPN_SPN_ACCESS_LVL,accessPolicies/$ACM_POLICY_NUMBER/accessLevels/OFFICE_CIDR_ACCESS_LVL \
--restricted-services=$VPC_SC_SERVICES_SCOPE \
--vpc-allowed-services=$VPC_SC_SERVICES_SCOPE \
--ingress-policies=${PROJECT_KEYWORD}-perimeter-ingress-policies.yaml \
--egress-policies=${PROJECT_KEYWORD}-perimeter-egress-policies.yaml \
--policy=$ACM_POLICY_NUMBER 
```

### 7.0.4. Retest Cloud Composer DAGs

Retest all the three DAG modules you created to ensure they work with the perimeter in place.

<hr>

This concludes the module, please proceed to the [next module](04-secure-cc2-iteration3-foundations.md).
