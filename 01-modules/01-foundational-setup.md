# About

This module covers the foundational one-site setup to start working on Data Analytics endeavors on GCP.

In this module, we will cover the folowing-<br>
[1. Pre-requisites]()<br>
[3. Enable requisite Google APIs for Project Indra](01-general.md#3-enable-requisite-google-apis)<br>
[4. Create a VPC, a subnet, firewall rules](01-general.md#4-create-a-vpc-a-subnet-firewall-rules)<br>
[5. Implement organizational policies](01-general.md#5-implement-organizational-policies)<br>
[6. Create a Service Account](01-general.md#6-create-a-service-account)<br>
[7. General IAM Permissions](01-general.md#7-grant-iam-permissions)<br>
[8. Cloud Composer Specific Permissions](01-general.md#8-permissions-specific-to-composer2)<br>
[9. Cloud Functions Specific Permissions](01-general.md#9-permissions-specific-to-cloud-functions)<br>
[10. Cloud Dataflow Specific Permissions](01-general.md#10-permissions-specific-to-cloud-dataflow)<br>
[11. Cloud Storage Specific Permissions](01-general.md#11-permissions-specific-to-cloud-storage)<br>
[12. IAM permissions Recap](01-general.md#12-permissions-recap)<br>


## Duration
~ 1 hour

## Dependencies
None, but the rest of the modules are dependent on this module being successfully completed.


## 1. Pre-requisites 

Create a GCP project. You will need administrator privileges to the organization and owner privileges for the project for the rest of the modules.<br>
<br>
The author's project is called "e2e-demo-indra"<br>
For the rest of the hands on lab, we will refer to the project as "e2e-demo-indra"<br>
<br>
From the cloud console project dashboard, capture the project number.<br>

![Dashboard](../00-images/00-00-dashboard.png)

<hr style="border:12px solid gray"> </hr>
<br>

## 2. Variables for use in the module

In Cloud Shell, lets create some variables we will use for the rest of the project-
```
PROJECT_NUMBER=914583619622  # Replace with your project's
PROJECT_ID=e2e-demo-indra  # Replace with your project's
UMSA="indra-sa"
UMSA_FQN=$UMSA@$PROJECT_ID.iam.gserviceaccount.com
ADMIN_FQ_UPN="admin@xxx.altostrat.com" # Replace with your Argolis UPN
```

## 3. Enable requisite Google APIs

Launch cloud shell, change scope to the project you created (if required), and run the below commands-

```
gcloud services enable orgpolicy.googleapis.com
gcloud services enable compute.googleapis.com
gcloud services enable container.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable composer.googleapis.com
gcloud services enable monitoring.googleapis.com 
gcloud services enable cloudtrace.googleapis.com 
gcloud services enable clouddebugger.googleapis.com 
gcloud services enable bigquery.googleapis.com 
gcloud services enable storage.googleapis.com
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable pubsub.googleapis.com
gcloud services enable dataflow.googleapis.com
gcloud services enable dns.googleapis.com
gcloud services enable sqladmin.googleapis.com
```


<hr style="border:12px solid gray"> </hr>
<br>



## 4. Update organizational policies

Applicable for Google Customer Engineers working in Argolis-

a) Create variables for use further in the rest of project in cloud shell

```
PROJECT_ID=e2e-demo-indra # Replace with yours if different
```

b) Relax require OS Login
```
rm os_login.yaml

cat > os_login.yaml << ENDOFFILE
name: projects/${PROJECT_ID}/policies/compute.requireOsLogin
spec:
  rules:
  - enforce: false
ENDOFFILE

gcloud org-policies set-policy os_login.yaml 

rm os_login.yaml
```

c) Disable Serial Port Logging

```

rm disableSerialPortLogging.yaml

cat > disableSerialPortLogging.yaml << ENDOFFILE
name: projects/${PROJECT_ID}/policies/compute.disableSerialPortLogging
spec:
  rules:
  - enforce: false
ENDOFFILE

gcloud org-policies set-policy disableSerialPortLogging.yaml 

rm disableSerialPortLogging.yaml

```

d) Disable Shielded VM requirement

```

shieldedVm.yaml 

cat > shieldedVm.yaml << ENDOFFILE
name: projects/$PROJECT_ID/policies/compute.requireShieldedVm
spec:
  rules:
  - enforce: false
ENDOFFILE

gcloud org-policies set-policy shieldedVm.yaml 

rm shieldedVm.yaml 

```

e) Disable VM can IP forward requirement

```
rm vmCanIpForward.yaml

cat > vmCanIpForward.yaml << ENDOFFILE
name: projects/$PROJECT_ID/policies/compute.vmCanIpForward
spec:
  rules:
  - allowAll: true
ENDOFFILE

gcloud org-policies set-policy vmCanIpForward.yaml

rm vmCanIpForward.yaml

```

f) Enable VM external access 

```

rm vmExternalIpAccess.yaml

cat > vmExternalIpAccess.yaml << ENDOFFILE
name: projects/$PROJECT_ID/policies/compute.vmExternalIpAccess
spec:
  rules:
  - allowAll: true
ENDOFFILE

gcloud org-policies set-policy vmExternalIpAccess.yaml

rm vmExternalIpAccess.yaml

```

g) Enable restrict VPC peering

```
rm restrictVpcPeering.yaml

cat > restrictVpcPeering.yaml << ENDOFFILE
name: projects/$PROJECT_ID/policies/compute.restrictVpcPeering
spec:
  rules:
  - allowAll: true
ENDOFFILE

gcloud org-policies set-policy restrictVpcPeering.yaml

rm restrictVpcPeering.yaml

```


h) Configure ingress settings for Cloud Functions

```
rm gcf-ingress-settings.yaml

cat > gcf-ingress-settings.yaml << ENDOFFILE
name: projects/$PROJECT_NUMBER/policies/cloudfunctions.allowedIngressSettings
spec:
  etag: CO2D6o4GEKDk1wU=
  rules:
  - allowAll: true
ENDOFFILE

gcloud org-policies set-policy gcf-ingress-settings.yaml

rm gcf-ingress-settings.yaml

```

i) Validation<br>
To describe a particular constratint, run like the below describes the constraint for cloud function ingress setting for the author's project-
```
gcloud org-policies describe \
cloudfunctions.allowedIngressSettings --project=e2e-demo-indra
```

Author's output:
```
name: projects/xxxnn/policies/cloudfunctions.allowedIngressSettings
spec:
  etag: CPz46Y4GELiOlfQB
  rules:
  - values:
      allowedValues:
      - ALLOW_ALL
  updateTime: '2022-01-09T06:11:08.512051Z'
  
 ```

<hr style="border:12px solid gray"> </hr>
<br>

## 5. Create a User Managed Service Account (UMSA)

We will use this UMSA as the runtime service account in the Data Analytics hands on labs that complement this repository-

```
gcloud iam service-accounts create ${UMSA} \
    --description="User Managed Service Account for the Indra E2E Project" \
    --display-name=$UMSA 
```

![UMSA-4](../00-images/00-04-UMSA-nav.png)
<br>
![UMSA-5](../00-images/00-05-UMSA.png)
<br>
<hr style="border:12px solid gray"> </hr>
<br>


## 6. Grant IAM Permissions 

### 6.1. Permissions specific to UMSA

#### 6.1.a. Service Account User role for UMSA

```
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member=serviceAccount:${UMSA_FQN} \
    --role=roles/iam.serviceAccountUser   
```

![UMSA-5](../00-images/00-05-UMSA.png)

#### 6.1.b. Service Account Token Creator role for UMSA

```
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member=serviceAccount:${UMSA_FQN} \
    --role=roles/iam.serviceAccountTokenCreator  
```

### 6.1.c. Permission for lab attendee to operate as the UMSA

```
gcloud iam service-accounts add-iam-policy-binding \
    ${UMSA_FQN} \
    --member="user:${ADMIN_FQ_UPN}" \
    --role="roles/iam.serviceAccountUser"
```

![UMSA-6](../00-images/00-06-UMSA-ActAs.png)


## 7. Permissions specific to Cloud Composer

### 7.a. Cloud Composer Administrator role for UMSA

```
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member=serviceAccount:${UMSA_FQN} \
    --role=roles/composer.admin
```

### 7.b. Cloud Composer Worker role for UMSA

```
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member=serviceAccount:${UMSA_FQN} \
    --role=roles/composer.worker
```

### 7.c. Cloud Composer ServiceAgentV2Ext role for Composer Google Managed Service Agent Account (CGMSAA)

This account is visible in IAM on Cloud Console only when the "Include Google Provided Role Grants" check box is checked.
This service accounts gets auto-created in the project when the Google API for Composer is enabled.

```
CGMSAA_FQN=service-${PROJECT_NUMBER}@cloudcomposer-accounts.iam.gserviceaccount.com

gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member=serviceAccount:${CGMSAA_FQN} \
    --role roles/composer.ServiceAgentV2Ext
```


### 7.d. Permissions for operator to be able to change configuration of Composer 2 environment and such

```
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member=user:${ADMIN_FQ_UPN} \
    --role roles/composer.admin

```

### 7.e. Permissions for operator to be able to manage the Composer 2 GCS buckets and environments


```
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
    --member=user:${ADMIN_FQ_UPN} \
    --role roles/composer.environmentAndStorageObjectViewer
```


<hr style="border:12px solid gray"> </hr>
<br>


## 8. Permissions specific to Cloud Functions

### 8.1. Permissions specific to UMSA

### 8.1.a. Permission for UMSA to operate as a GCF service agent

```
gcloud projects add-iam-policy-binding ${PROJECT_ID} --member=serviceAccount:$UMSA_FQN --role=roles/cloudfunctions.serviceAgent
```

### 8.1.b. Permission for UMSA to operate as a GCF admin

```
gcloud projects add-iam-policy-binding ${PROJECT_ID} --member=serviceAccount:$UMSA_FQN --role=roles/cloudfunctions.admin
```


<hr style="border:12px solid gray"> </hr>
<br>
<br>


## 9. Permissions specific to Cloud Dataflow

### 9.1. Permissions for UMSA to spawn Cloud Dataflow pipelines

a) Dataflow worker
```
gcloud projects add-iam-policy-binding ${PROJECT_ID} --member=serviceAccount:$UMSA_FQN --role=roles/dataflow.worker
```

b) To Dataflow developer
```
gcloud projects add-iam-policy-binding ${PROJECT_ID} --member=serviceAccount:$UMSA_FQN --role=roles/dataflow.worker
``` 

## 10. Permissions specific to Cloud Storage

### 10.1. Permissions for UMSA to read from GCS

a) ObjectViewer
```
gcloud projects add-iam-policy-binding $PROJECT_ID --member=serviceAccount:$UMSA_FQN --role="roles/storage.objectViewer"
```

## 11. Permissions recap

Go to the Cloud Console and navigate to the IAM -> IAM & Admin and ensure you check the "Include Google Provided Role Grants". Screenshots of what you should expect are below.

## 11.1. The lab attendee permissions
![01-03-14](../00-images/01-03-14.png)
<br>

## 11.2. The UMSA permissions
![01-03-14](../00-images/01-03-15.png)
<br>

## 11.3. The Cloud Composer Service Agent Account permissions
![01-03-16](../00-images/01-03-16.png)
<br>

## 11.4. The various Google Managed Default Service Accounts
![01-03-17](../00-images/01-03-17.png)
<br>
<br>

![01-03-18](../00-images/01-03-18.png)
<br>

<hr>
This concludes the module. 
