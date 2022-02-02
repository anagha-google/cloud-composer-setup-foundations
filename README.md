# Cloud Composer Provisioning Foundations for Data Analytics Endeavors

## About the Repository
This repository contains hands-on-lab modules that cover provisioning the foundational infrastructure and security in GCP for Cloud Composer 2 based Data Analytics projects. It does not cover authoring complex Apache Airflow DAGs and Airflow functionality.

## Motivation and Audience
Simplify the journey of a Data Analytics Architect/Engineer persona on GCP, by educating on the intricacies of foundational setup, unblocking and improving speed to productivity in their core competency (analytics). For the GCP Customer Engineer, the hands on labs cover provisioning in **Argolis**. 

## Structure
The repository contains modules that are deliberately detailed with sequential steps (versus fully scripted, automated) to provide an understanding of what is involved. The hands on lab modules will be complemented with Terraform scripts for automation.


## Table of Contents

### Module 1: Walk through of Cloud Composer DAGs and associated code

The DAGs are embarassigly basic to maintain focus on environment provisioning, stability and securing.

| # | Sub-Modules | 
| -- | :--- |
| 1 | Git repo cloning | 
| 2 | Walk through of a Hello World DAG |
| 3 | Walk through of GCS Event Driven Orchestration of the Hello World DAG |
| 4 | Walk through of Pub/Sub Event Driven Orchestration of the Hello World DAG |
| 5 | Walk through of a slightly more realistic DAG with GCS, Cloud Dataflow and BigQuery |

### Module 2: Public Cloud Composer 2 cluster setup

This module includes the below sub-modules, is standalone and is available in a separate [repo](https://github.com/anagha-google/composer2-basic-orchestration). This setup is recommended for kicking tires, simple demos, but is **not a secure setup**. It is recommended that you run through this module if you are new to Cloud Composer 2 and its provisioning, new to authoring, deploying DAGs, and triggering DAG execution in a event driven fashion. <br>

If you need to start with a secure Cloud Composer 2 setup, jump to module 3, below. The same DAGs in module 1, are used across modules.

| # | Sub-Modules | 
| -- | :--- |
| 1 | Foundational setup - network, subnet, org policies, IAM permissions etc | 
| 2 | Provision Cloud Composer 2 |
| 3 | Deploy and test a Hello World DAG |
| 4 | Deploy and test GCS Event Driven Orchestration of the Hello World DAG |
| 5 | Deploy and test Pub/Sub Event Driven Orchestration of the Hello World DAG |
| 6 | Deploy and test Time Event Driven Orchestration of the Hello World DAG |
| 7 | Deploy and test a more realistic DAG with GCS, Cloud Dataflow and BigQuery |


### Module 3: Foundational One-time Setup Lab for a secure Cloud Composer 2 deployment

[Jump to lab module](01-modules/03-foundational-setup.md)

| # | Sub-module | 
| -- | :---    |
| 1 | Create a (service) project for Data Analytics | 
| 2 | Enable requisite Google APIs |  
| 3 | Update organizational policies | 
| 4 | Create a User Managed Service Account for Data Analytics | 
| 5 | Grant general IAM permissions | 
| 6 | Cloud Composer specific IAM permissions | 
| 7 | Cloud Functions specific IAM permissions | 
| 8 | Cloud Dataflow specific IAM permissions | 
| 9 | Cloud Storage specific IAM permissions | 
| 10 | BigQuery specific IAM permissions | 


### Module 4: Secure Cloud Composer 2 setup - iteration 1

This module covers the following security features/components/layers-

| # | Module | 
| -- | :---    | 
| 1 | ..|  

### Module 5: Secure Cloud Composer 2 setup - iteration 2

This module adds VPC-SC and PSC to the setup in module 4.

| # | Module | 
| -- | :---    | 
| 1 | ..|  


## Credits
This is a community contribution. <br>


| # | Contributor | Contribution | About |
| -- | :---    | :---| :---| 
| 1 | Anagha Khanolkar | Primary Author | Data Analytics Specialist, Google Cloud |
| 2 | Jay O' Leary | Testing | Data Analytics Specialist, Google Cloud |
