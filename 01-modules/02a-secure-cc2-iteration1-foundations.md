# About

This module covers creation of a Shared VPC, subnets, requisite organizational policies, associated firewall rules, associated IAM permissions, DNS entries, in preparation of a secure and realistic Cloud Composer setup.<br>

Shared VPC enables organizations to establish budgeting and access control boundaries at the project level while allowing for secure and efficient communication using private IPs across those boundaries. In the Shared VPC configuration, Cloud Composer can invoke services hosted in other Google Cloud projects in the same organization without exposing services to the public internet.

<br>
Shared VPC requires that you designate a host project to which networks and subnetworks belong and a service project, which is attached to the host project. When Cloud Composer participates in a Shared VPC, the Cloud Composer environment is in the service project.<br><br>

To set up Shared VPC, you will need to pre-define the following IP ranges in the host project:

- Primary IP Range of the subnet used by GKE nodes that Cloud Composer uses as its Compute Engine layer.
- Secondary IP Range for GKE services.
- Secondary IP Range for GKE pods.
- Secondary IP Ranges cannot overlap with any other secondary ranges in this VPC.
And ensure that secondary ranges are large enough to accommodate the cluster's size and your environment scaling.<br><br>

[GCP Documentation for Cloud Composer 2 with Shared VPC](https://cloud.google.com/composer/docs/composer-2/configure-shared-vpc)<br>
Sub-module dependencies: Successful completion of [foundational setup](01-foundational-setup.md).
<hr>

## 1. Create a project for "Shared VPC" called zeus-host-proj 

Create a new project for the shared VPC.
<br>
<hr>

## 2. Variables for use in the sub-module

In cloud shell scoped to the shared VPC/host project, paste the following variables after **updating the same to match your environment**-
```
ORG_ID=akhanolkar.altostrat.com #Replace with yours
ORG_ID_NBR=236589261571 #Replace with yours

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
SHARED_VPC_CONNECTOR_SNET_CIDR=10.70.0.0/28

SHARED_VPC_CC2_SNET_CIDR_BLK='10.65.61.0/24' # Number of GKE nodes and ILBs available 
CC2_PODS_CIDR_BLK='10.66.0.0/16' # Composer pods, ensure sufficient, especially for autoscale
CC2_SVCS_CIDR_BLK='10.67.0.0/16' # Composer pods, ensure sufficient, especially for autoscale
GKE_CNTRL_PLN_CIDR_BLK='10.65.62.0/24' 
CC2_CIDR_BLK='10.65.63.0/24' 
CSQL_CIDR_BLK='10.65.64.0/24'

OFFICE_CIDR=98.222.97.10/32 # Replace with your CIDR
```

<br>
<hr>

## 3. Enable Google APIs in the shared VPC host project

In cloud shell scoped to the shared VPC/host project, run the commands below-

```
gcloud services enable container.googleapis.com --project $SHARED_VPC_HOST_PROJECT_ID
gcloud services enable orgpolicy.googleapis.com --project $SHARED_VPC_HOST_PROJECT_ID
gcloud services enable dns.googleapis.com --project $SHARED_VPC_HOST_PROJECT_ID 
gcloud services enable vpcaccess.googleapis.com --project $SHARED_VPC_HOST_PROJECT_ID 
```

<br>
<hr>


## 4. Apply organizational policies for the shared VPC host project

*Ensure you are authorized to apply organization policies - have the org policy admin role.*<br>

In cloud shell scoped to the shared VPC/host project, run the below:

a) Restricted VPC peering related
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

b) IP forwarding related
```
rm vmCanIpForward.yaml

cat > vmCanIpForward.yaml << ENDOFFILE
name: projects/$SHARED_VPC_HOST_PROJECT_ID/policies/compute.vmCanIpForward
spec:
  rules:
  - allowAll: true
ENDOFFILE

gcloud org-policies set-policy vmCanIpForward.yaml

rm vmCanIpForward.yaml

```

c) Relax require OS Login
```
rm os_login.yaml

cat > os_login.yaml << ENDOFFILE
name: projects/${SHARED_VPC_HOST_PROJECT_ID}/policies/compute.requireOsLogin
spec:
  rules:
  - enforce: false
ENDOFFILE

gcloud org-policies set-policy os_login.yaml 

rm os_login.yaml
```

d) Disable Serial Port Logging

```
rm disableSerialPortLogging.yaml

cat > disableSerialPortLogging.yaml << ENDOFFILE
name: projects/${SHARED_VPC_HOST_PROJECT_ID}/policies/compute.disableSerialPortLogging
spec:
  rules:
  - enforce: false
ENDOFFILE

gcloud org-policies set-policy disableSerialPortLogging.yaml 

rm disableSerialPortLogging.yaml
```

e) Disable Shielded VM requirement

```
shieldedVm.yaml 

cat > shieldedVm.yaml << ENDOFFILE
name: projects/$SHARED_VPC_HOST_PROJECT_ID/policies/compute.requireShieldedVm
spec:
  rules:
  - enforce: false
ENDOFFILE

gcloud org-policies set-policy shieldedVm.yaml 

rm shieldedVm.yaml 
```

f) Add the project that sources the Serverless VPC connector image as trusted

```
rm trustedImagesPolicy.yaml

gcloud resource-manager org-policies describe \
   compute.trustedImageProjects --project=$SHARED_VPC_HOST_PROJECT_ID \
   --effective > trustedImagesPolicy.yaml

echo "  - projects/serverless-vpc-access-images" >> trustedImagesPolicy.yaml

gcloud resource-manager org-policies set-policy \
   trustedImagesPolicy.yaml --project=$SHARED_VPC_HOST_PROJECT_ID
   
   
rm trustedImagesPolicy.yaml
```

<br>
<hr>

## 5. Grant IAM role to the admininstrator (or yourself), to create a "Shared VPC"

In cloud shell scoped to the shared VPC/host project, run the below:
```
gcloud organizations add-iam-policy-binding $ORG_ID_NBR \
  --member=user:$ADMIN_UPN_FQN \
  --role="roles/compute.xpnAdmin"
```

<br>
<hr>

## 6. Enable shared VPC for the "Shared VPC" project

In cloud shell scoped to the shared VPC/host project, run the below:
```
gcloud compute shared-vpc enable $SHARED_VPC_HOST_PROJECT_ID
```

<br>
<hr>

## 7. Associate your data analytics project with the "Shared VPC" project

In cloud shell scoped to the shared VPC/host project, run the below:
```
gcloud compute shared-vpc associated-projects add $SVC_PROJECT_ID \
    --host-project $SHARED_VPC_HOST_PROJECT_ID
```

<br>
<hr>

## 8. Review IP range considerations for Cloud Composer 2

A core requirement here is to ensure there is no CIDR range overlap between your ranges and the Google services
<br>Review the documentation [here](
https://cloud.google.com/composer/docs/composer-2/configure-private-ip#step_1_check_network_requirements)

<br>
<hr>

## 9. Create a VPC in the "shared VPC" project

In cloud shell scoped to the shared VPC/host project, run the below:
```
gcloud compute networks create $SHARED_VPC_NETWORK_NM \
--project=$SHARED_VPC_HOST_PROJECT_ID \
--subnet-mode=custom \
--mtu=1460 \
--bgp-routing-mode=regional
```

<br>
<hr>

## 10. Create subnets for secure Cloud Composer 2 & for a shared VPC Access Connector

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

### 10.1. Create subnet for CC2

In cloud shell scoped to the shared VPC/host project, run the below:
```
gcloud compute networks subnets create $SHARED_VPC_CC2_SNET_NM \
 --network $SHARED_VPC_NETWORK_NM \
 --range $SHARED_VPC_CC2_SNET_CIDR_BLK \
 --region $LOCATION \
 --enable-private-ip-google-access \
 --project $SHARED_VPC_HOST_PROJECT_ID 
```

### 10.2. Update CC2 subnet to add a second  secondary IP range - for composer pods
*As of the authoring of this guide (Jan 14, 2022), the secondary IP range name had to strictly be composer-pods.*<br>
In cloud shell scoped to the shared VPC/host project, run the below:
```
 gcloud compute networks subnets update $SHARED_VPC_CC2_SNET_NM \
 --region $LOCATION \
 --add-secondary-ranges composer-pods=$CC2_PODS_CIDR_BLK
```

### 10.3. Update CC2 subnet to add asecond  secondary IP range - for composer services
*As of the authoring of this guide (Jan 14, 2022), the secondary IP range name had to strictly be composer-services*<br>
In cloud shell scoped to the shared VPC/host project, run the below:
```
 gcloud compute networks subnets update $SHARED_VPC_CC2_SNET_NM \
 --region $LOCATION \
 --add-secondary-ranges composer-services=$CC2_SVCS_CIDR_BLK
```

### 10.4 Other CC2 related secondary IP ranges
The other secondary IP ranges listed in the variables should not be created, but **reserved** for Cloud Composer 2 secure deployment lab sub-module and will be used at environment provisioning time.

<br>
<hr>

### 10.5. Create a subnet for the shared VPC access connector
In cloud shell scoped to the shared VPC/host project, run the below:
```
gcloud compute networks subnets create $SHARED_VPC_CONNECTOR_SNET_NM \
 --network $SHARED_VPC_NETWORK_NM \
 --range $SHARED_VPC_CONNECTOR_SNET_CIDR \
 --region $LOCATION \
 --enable-private-ip-google-access \
 --project $SHARED_VPC_HOST_PROJECT_ID 
```

Describe and ensure private
```
gcloud compute networks subnets describe $SHARED_VPC_CONNECTOR_SNET_NM
```

Author's output-
```
gcloud compute networks subnets describe $SHARED_VPC_CONNECTOR_SNET_NM
Did you mean region [us-central1] for subnetwork: [zeus-vpc-cnctr-snet] (Y/n)?  y

creationTimestamp: '2022-01-28T14:56:32.860-08:00'
fingerprint: gaWbylk4EZs=
gatewayAddress: 10.70.0.1
id: '1454704618911681103'
ipCidrRange: 10.70.0.0/28
kind: compute#subnetwork
name: zeus-vpc-cnctr-snet
network: https://www.googleapis.com/compute/v1/projects/zeus-host-proj/global/networks/zeus-shared-vpc
privateIpGoogleAccess: true
privateIpv6GoogleAccess: DISABLE_GOOGLE_ACCESS
purpose: PRIVATE
region: https://www.googleapis.com/compute/v1/projects/zeus-host-proj/regions/us-central1
selfLink: https://www.googleapis.com/compute/v1/projects/zeus-host-proj/regions/us-central1/subnetworks/zeus-vpc-cnctr-snet
stackType: IPV4_ONLY
```

## 11. Create firewall rules


### 11.1. Allow egress from GKE Node IP range to any destination (0.0.0.0/0), TCP/UDP port 53

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

### 11.2. Allow egress from GKE Node IP range to GKE Node IP range, all ports

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

### 11.3. Allow egress from GKE Node IP range to GKE Pods IP range, all ports

In cloud shell scoped to the shared VPC/host project, run the below:
```
gcloud compute firewall-rules create allow-to-gke-pod-sipr-egress \
    --network $SHARED_VPC_NETWORK_NM \
    --action allow \
    --direction egress \
    --rules ALL \
    --destination-ranges $CC2_PODS_CIDR_BLK \
    --priority 1000 
```

### 11.4. Allow egress from GKE Node IP range to GKE Control Plane IP range, all ports

In cloud shell scoped to the shared VPC/host project, run the below:
```
gcloud compute firewall-rules create allow-to-gke-ctrl-pln-sipr-egress \
    --network $SHARED_VPC_NETWORK_NM \
    --action allow \
    --direction egress \
    --rules ALL \
    --destination-ranges $GKE_CNTRL_PLN_CIDR_BLK \
    --priority 1000 
```

### 11.5. Allow ingress from GCP Health Checks 130.211.0.0/22, 35.191.0.0/16 to GKE Node IP range, TCP ports 80 and 443.

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

### 11.6. Allow egress from GKE Node IP range to GCP Health Checks 130.211.0.0/22, 35.191.0.0/16, TCP ports 80 and 443.

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

### 11.7. Allow egress from GKE Node IP range to Cloud Composer network IP range, TCP ports 3306 and 3307.

In cloud shell scoped to the shared VPC/host project, run the below:
```
gcloud compute firewall-rules create allow-to-cc2-sipr-egress \
    --network $SHARED_VPC_NETWORK_NM \
    --action allow \
    --direction egress \
    --destination-ranges $CC2_CIDR_BLK \
    --rules tcp:3306,tcp:3307 \
    --priority 1000 
```

### 11.8. Allow yourself access


In cloud shell scoped to the shared VPC/host project, run the below:
```
gcloud compute firewall-rules create allow-all-to-office-cidr \
--direction=INGRESS \
--priority=1000 \
--network=$SHARED_VPC_NETWORK_NM \
--action=ALLOW \
--rules=all \
--source-ranges=$OFFICE_CIDR
```

### 11.9. Serverless VPC Access Connector related firewall rules

In cloud shell scoped to the shared VPC/host project, run the below.<br>
The following three commands are the rules to allow requests from serverless environments (Cloud Functions, Cloud Run etc) to reach all VPC Connectors in the network:


```
gcloud compute firewall-rules create serverless-to-vpc-connector \
--allow tcp:667,udp:665-666,icmp \
--source-ranges 107.178.230.64/26,35.199.224.0/19 \
--direction=INGRESS \
--target-tags vpc-connector \
--network=$SHARED_VPC_NETWORK_NM

gcloud compute firewall-rules create vpc-connector-to-serverless \
--allow tcp:667,udp:665-666,icmp \
--destination-ranges 107.178.230.64/26,35.199.224.0/19 \
--direction=EGRESS \
--target-tags vpc-connector \
--network=$SHARED_VPC_NETWORK_NM

gcloud compute firewall-rules create vpc-connector-health-checks \
--allow tcp:667 \
--source-ranges 130.211.0.0/22,35.191.0.0/16,108.170.220.0/23 \
--direction=INGRESS \
--target-tags vpc-connector \
--network=$SHARED_VPC_NETWORK_NM

```

Next, create an ingress rule on your VPC network to allow requests from connectors:
```
gcloud compute firewall-rules create vpc-connector-requests \
--allow tcp,udp,icmp \
--direction=INGRESS \
--source-tags vpc-connector \
--network=$SHARED_VPC_NETWORK_NM
```

<br>
<hr>


## 12. Configure DNS - connectivity to *.pkg.dev

In cloud shell scoped to the host project, run the below to cnfigure connectivity-

### 12.1. Create a zone for pkg.dev
```
gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID managed-zones create pkg-dev --description="" \
--dns-name="pkg.dev." \
--visibility="private" \
--networks=$SHARED_VPC_NETWORK_NM
```

### 12.2. Create a A record

```
gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID record-sets transaction \
start --zone="pkg-dev" && gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID record-sets transaction \
add 199.36.153.4 199.36.153.5 199.36.153.6 199.36.153.7 --name="pkg.dev." --ttl="300" --type="A" --zone="pkg-dev"  && gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID record-sets transaction \
execute --zone="pkg-dev"
```


### 12.3. Create a CNAME record


```
gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID \
record-sets transaction start --zone="pkg-dev" && gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID record-sets transaction \
add pkg.dev. --name="*.pkg.dev." --ttl="300" --type="CNAME" --zone="pkg-dev" && gcloud beta dns --project=$SHARED_VPC_HOST_PROJECT_ID record-sets transaction \
execute --zone="pkg-dev"
```


## 13. Grant IAM permissions to host project for service project's service accounts

### 13.1. Service project's Google APIs default service account specific IAM permissions
In the host project, edit permissions for the Google APIs service account, SERVICE_PROJECT_NUMBER@cloudservices.gserviceaccount.com. For this account, add another role, compute.networkUser at the project level. This is a requirement for managed instance groups used with Shared VPC because this type of service account performs tasks such as instance creation.<br>

In cloud shell scoped to the shared VPC/host project, run the below.<br>

```
SVC_PROJECT_GOOGLE_API_GMSA=$SVC_PROJECT_NUMBER@cloudservices.gserviceaccount.com

gcloud projects add-iam-policy-binding ${SHARED_VPC_HOST_PROJECT_ID} \
    --member=serviceAccount:${SVC_PROJECT_GOOGLE_API_GMSA} \
        --role=roles/compute.networkUser 
```

### 13.2. Grant service project's GKE default service account specific IAM permissions

In this step, we will grant IAM permissions in the host project, for the GKE defaukt Google Managed Service Account from service project.

<br><br>
In cloud shell scoped to the host/shared VPC project, run the below-
```
SVC_PROJECT_GKE_GMSA=service-$SVC_PROJECT_NUMBER@container-engine-robot.iam.gserviceaccount.com
```

In the host project, edit permissions for the GKE service accounts, service-SERVICE_PROJECT_NUMBER@container-engine-robot.iam.gserviceaccount.com.
For the service account, add another role, **compute.networkUser**. Grant this role at the subnet level to allow a service account to set up the VPC peerings required by Cloud Composer. As an alternative, you can grant this role for the whole host project. In this case, the service project's GKE service account has permissions to use any subnet in the host project.
```
gcloud projects add-iam-policy-binding ${SHARED_VPC_HOST_PROJECT_ID} \
    --member=serviceAccount:${SVC_PROJECT_GKE_GMSA} \
    --role=roles/compute.networkUser 
```

In the host project, edit permissions for the GKE Service Account of the service project. For this account, add another role, **Host Service Agent User**.
This allows the GKE Service Account of the service project to use the GKE Service Account of the host project to configure shared network resources.
```
gcloud projects add-iam-policy-binding ${SHARED_VPC_HOST_PROJECT_ID} \
    --member=serviceAccount:${SVC_PROJECT_GKE_GMSA} \
    --role roles/container.hostServiceAgentUser
```

### 13.3. Create Composer Agent Service Account in "Shared VPC" project

In the host project, **if this is the first Cloud Composer environment**, provision the Composer Agent Service Account 

```
gcloud beta services identity create --service=composer.googleapis.com
```


### 13.4. Grant IAM permissions in the host project for the service project's Cloud Composer 2 default service account 

In cloud shell scoped to the shared VPC/host project, run the below. 
```
SVC_PROJECT_CC2_GMSA=service-$SVC_PROJECT_NUMBER@cloudcomposer-accounts.iam.gserviceaccount.com
```

Grant **Compute Network User** role
```
gcloud projects add-iam-policy-binding ${SHARED_VPC_HOST_PROJECT_ID} \
    --member=serviceAccount:${SVC_PROJECT_CC2_GMSA} \
        --role=roles/compute.networkUser 
```  

Grant **Composer Shared VPC Agent** role
```
gcloud projects add-iam-policy-binding ${SHARED_VPC_HOST_PROJECT_ID} \
    --member=serviceAccount:${SVC_PROJECT_CC2_GMSA} \
        --role=roles/composer.sharedVpcAgent 
```  
 

### 13.5. Grant IAM permissions in the host project for the service project's User Managed Service Account

In cloud shell scoped to the shared VPC/host project, run the below.<br>
```
gcloud projects add-iam-policy-binding ${SHARED_VPC_HOST_PROJECT_ID} \
    --member=serviceAccount:${SVC_PROJECT_UMSA_FQN} \
    --role=roles/compute.networkUser 
```

### 13.6. Grant IAM permissions in the host project for the service project's Google Managed Cloud Dataflow service account 

In cloud shell scoped to the shared VPC/host project, run the below.<br>
```
SVC_PROJECT_CDF_GMSA=service-$SVC_PROJECT_NUMBER@dataflow-service-producer-prod.iam.gserviceaccount.com

gcloud projects add-iam-policy-binding ${SHARED_VPC_HOST_PROJECT_ID} \
    --member=serviceAccount:${SVC_PROJECT_CDF_GMSA} \
    --role=roles/compute.networkUser 
```

### 13.7. Grant Serverless VPC Access Connector related IAM permissions

For each service project that will use VPC Connectors, a Shared VPC Admin must grant the Compute Network User role (compute.networkUser) in the host project to the service project cloudservices and vpcaccess service accounts.


In cloud shell scoped to the shared VPC/host project, run the below.<br>
```
gcloud projects add-iam-policy-binding $SHARED_VPC_HOST_PROJECT_ID \
--role "roles/compute.networkUser" \
--member "serviceAccount:service-$SVC_PROJECT_NUMBER@gcp-sa-vpcaccess.iam.gserviceaccount.com"


gcloud projects add-iam-policy-binding $SHARED_VPC_HOST_PROJECT_ID \
--role "roles/compute.networkUser" \
--member "serviceAccount:$SVC_PROJECT_NUMBER@cloudservices.gserviceaccount.com"
```

The individual deploying the connector needs compute security admin role in the host project-
```
gcloud projects add-iam-policy-binding ${SHARED_VPC_HOST_PROJECT_ID} \
  --member=user:$ADMIN_UPN_FQN \
  --role=roles/compute.securityAdmin
```

The service accounts needing VCP connector access require permissions
```

gcloud projects add-iam-policy-binding ${SHARED_VPC_HOST_PROJECT_ID} \
--member=serviceAccount:service-${SVC_PROJECT_NUMBER}@gcf-admin-robot.iam.gserviceaccount.com \
--role=roles/vpcaccess.user

gcloud projects add-iam-policy-binding ${SHARED_VPC_HOST_PROJECT_ID}  \
--member serviceAccount:${SVC_PROJECT_UMSA_FQN} \
--role roles/vpcaccess.user
```



<br>
<hr>

## 14. Create the Serverless VPC Access Connector

Docs: https://cloud.google.com/compute/docs/images/restricting-image-access<br>

In cloud shell scoped to the shared VPC/host project, run the below-<br>
```
gcloud compute networks vpc-access connectors create zeus-gcf-vpc-cnnctr \
--region $LOCATION \
--subnet $SHARED_VPC_CONNECTOR_SNET_NM \
--subnet-project $SHARED_VPC_HOST_PROJECT_ID \
--min-instances 2 \
--max-instances 3 \
--machine-type f1-micro
```

<br>
<hr>

## 15. Configure networking to allow downloads of external package 
This is specific to opening up a private cluster for downloading from Maven/PyPi/CRAN for DAGs in Cloud Composer 2 and/or in Cloud Dataflow DAGs referenced within<br>

### 15.1. Cloud Router setup

Docs: https://cloud.google.com/network-connectivity/docs/router/how-to/creating-routers<br>
In cloud shell scoped to the shared VPC/host project, run the below.<br>
```
gcloud compute routers create zeus-router-shared \
    --project=$SHARED_VPC_HOST_PROJECT_ID \
    --network=$SHARED_VPC_NETWORK_NM \
    --asn=65000 \
    --region=$LOCATION
```
    
### 15.2. Cloud NAT setup
Docs: https://cloud.google.com/nat/docs/gke-example#create-nat<br>
In cloud shell scoped to the shared VPC/host project, run the below.<br>
```
gcloud compute routers nats create zeus-nat-shared \
    --router=zeus-router-shared \
    --auto-allocate-nat-external-ips \
    --nat-all-subnet-ip-ranges \
    --enable-logging \
    --region=$LOCATION
```
<hr><br>
