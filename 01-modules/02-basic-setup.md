## 4. Create a VPC, a subnet, firewall rules

Launch cloud shell, change scope to the project you created (if required), and run the commands below to create the networking entities required for the hands on lab.


#### 4.1. Create a VPC

a) Create the network
```
gcloud compute networks create indra-vpc \
    --subnet-mode=custom \
    --bgp-routing-mode=regional \
    --mtu=1500
```

b) List VPCs with:
```
gcloud compute networks list
```

c) Describe your network with:
```
gcloud compute networks describe indra-vpc
```

d) View in the Cloud Console

![VPC](../01-images/00-01-vpc.png)
<br>

#### 4.2. Create a subnet for composer, dataflow and dataproc each

a) Create subnet for Composer2
```
gcloud compute networks subnets create indra-composer2-snet \
     --network=indra-vpc \
     --range=10.0.0.0/24 \
     --region=us-central1 \
     --enable-private-ip-google-access
```

b) Create subnet for Dataflow
```
gcloud compute networks subnets create indra-dataflow-snet \
     --network=indra-vpc \
     --range=10.0.1.0/24 \
     --region=us-central1 \
     --enable-private-ip-google-access
```

c) Create subnet for Dataproc
```
gcloud compute networks subnets create indra-dataproc-snet \
     --network=indra-vpc \
     --range=10.0.2.0/24 \
     --region=us-central1 \
     --enable-private-ip-google-access
```

![SNET](../01-images/00-02-snet.png)
<br>

#### 4.3. Create firewall rules

a) Intra-VPC, allow all communication

```
gcloud compute firewall-rules create allow-all-intra-vpc --project=e2e-demo-indra --network="projects/e2e-demo-indra/global/networks/indra-vpc" --description="Allows\ connection\ from\ any\ source\ to\ any\ instance\ on\ the\ network\ using\ custom\ protocols." --direction=INGRESS --priority=65534 --source-ranges=10.0.0.0/20 --action=ALLOW --rules=all
```

b) Allow SSH

```
gcloud compute firewall-rules create allow-all-ssh --project=e2e-demo-indra --network="projects/e2e-demo-indra/global/networks/indra-vpc" --description="Allows\ TCP\ connections\ from\ any\ source\ to\ any\ instance\ on\ the\ network\ using\ port\ 22." --direction=INGRESS --priority=65534 --source-ranges=0.0.0.0/0 --action=ALLOW --rules=tcp:22
```

c) Create a firewall rule to allow yourself to ingress

Replace with your IP address below-
```
gcloud compute --project=e2e-demo-indra firewall-rules create allow-all-to-my-machine --direction=INGRESS --priority=1000 --network=indra-vpc --action=ALLOW --rules=all --source-ranges=xx.xxx.xx.xx
```

d) Validate in Cloud Console

![FIREWALL](../01-images/00-03-firewall.png)
<br>

<hr style="border:12px solid gray"> </hr>
<br>
