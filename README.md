# Cloud Composer Provisioning Foundations for Data Analytics Endeavors

## About the Repository
This repository contains hands-on-lab modules that cover provisioning the foundational infrastructure and security in GCP for Cloud Composer based Data Analytics projects. It does not cover authoring complex Apache Airflow DAGs and Airflow functionality as the focus is creating a stable and secure environment for authoring pipelines.

## Motivation and Audience
Simplify the journey of a Data Analytics Architect/Engineer persona on GCP, by educating on the intricacies of foundational setup, unblocking and improving speed to productivity in their core competency (analytics). For the GCP Customer Engineer, the hands on labs cover provisioning in **Argolis**. 

## Structure
The repository contains modules that are deliberately detailed with sequential steps (versus fully scripted, automated) to provide an understanding of what is involved. The hands on lab modules will be complemented with Terraform scripts for automation.


## Table of Contents

### Section 1: Public Cloud Composer cluster setup

This module is available in a separate [repo](https://github.com/anagha-google/composer2-basic-orchestration). This setup is recommended for kicking tires, simple demos, but is **not a secure setup**. It is recommended that you run through this module if you are new to Cloud Composer 2 and its provisioning, new to authoring, deploying DAGs, and triggering DAG execution in a event driven fashion. <br>

If you need to start with a secure Cloud Composer 2 setup, jump to section 2, below. The same DAGs in section 2, are used across public/private Cloud Composer provisioning modules.

### Section 2: Cloud Composer DAGs used in the lab modules 

The DAGs are deliberately embarassigly basic to maintain focus on environment provisioning->securing->testing.

| # | Sub-Modules | 
| -- | :--- |
| 1 | Git repo cloning | 
| 2 | Hello World DAG |
| 3 | GCS Event Driven Orchestration of the Hello World DAG |
| 4 | Pub/Sub Event Driven Orchestration of the Hello World DAG |
| 5 | Minimum viable (ETL) DAG with GCS, Cloud Dataflow and BigQuery |


### Module 1: Foundational One-time Setup Lab for a secure Cloud Composer 2 deployment

[Jump to lab module](01-modules/01-foundational-setup.md)

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


### Module 2: Secure Cloud Composer setup - iteration 1

This module covers the following security features/components/layers-

| # | Module | 
| -- | :---    | 
| 1 | ..|  

### Module 3: Secure Cloud Composer setup - iteration 2

This module covers provisioning a secure Cloud Composer environment and testing scheduled as well as event driven orchestration of a "Hello World" DAG, followed by a minimum viable data pipeline/DAG.

| # | Module | 
| -- | :---    | 
| 1 | ..|  

### Module 4: Secure Cloud Composer setup - iteration 2

This module adds VPC Service Controls (VPC-SC) to the setup in module 3.

| # | Module | 
| -- | :---    | 
| 1 | ..| 


### Module 5: Secure Cloud Composer 2 setup - iteration 3

This module adds Private Service Connect (PSC) to the setup in module 4.

| # | Module | 
| -- | :---    | 
| 1 | ..| 


## Credits
This is a community contribution. <br>


| # | Contributor | Contribution | About |
| -- | :---    | :---| :---| 
| 1 | Anagha Khanolkar | Primary Author | Data Analytics Specialist, Google Cloud |
| 2 | Jay O' Leary | Testing | Data Analytics Specialist, Google Cloud |
