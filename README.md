# Cloud Composer 2 Provisioning Foundations for Data Analytics Endeavors

## About the Repository
This repository includes hands-on-lab modules that cover provisioning the foundational infrastructure and security in GCP for Cloud Composer 2 based Data Analytics projects. 

## Motivation and Audience
Simplify the journey of a Data Analytics Architect/Engineer persona on GCP, by educating on intricacies of foundational setup, unblocking and improving speed to productivity in their core competency. For the GCP Customer Engineer, the hands on labs cover provisioning in **Argolis**.

## Structure
The repository contains modules that are deliberately detailed with sequential steps (versus fully scripted, automated) to provide an understanding of what is involved.

## Prerequisites
Read the 


## Table of Contents

### Module 1: Walk through of Cloud Composer DAGs and associated code


### Module 2: Public Cloud Composer 2 cluster setup

This module includes the below sub-modules, is standalone and is available in a separate [repo](https://github.com/anagha-google/composer2-basic-orchestration).<br>
This setup is recommended for kicking tires, simple demps, but is **not a secure setup**. It is recommended that you run through this module if you are new to Clooud Composer 2 and its provisioning, new to authoring, deploying DAGs, and triggering DAG execution in a event driven fashion. <br>

If you need to start with a secure Cloud Composer 2 cluster, skip to module 3, below. The same DAGs in module 1, are used across modules.

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

[Jump to lab module](01-modules/01-foundational-setup.md)

| # | Sub-module | 
| -- | :---    |
| 1 | Enable requisite Google APIs |  
| 2 | Update organizational policies | 
| 3 | Create a User Managed Service Account for Data Analytics | 
| 4 | Grant general IAM permissions | 
| 5 | Cloud Composer specific IAM permissions | 
| 6 | Cloud Functions specific IAM permissions | 
| 7 | Cloud Dataflow specific IAM permissions | 
| 8 | Cloud Storage specific IAM permissions | 



### Module 3: Securing Cloud Composer 2 - iteration 1

This module includes creating and using a shared VPC, subnet, firewall rules, private Cloud Composer 2 cluster, authorized networks, secured Airflow website, private Dataflow cluster, DNS entries, user managed service account for provisioning Cloud Composer 2, as the run tie account for DAGs, for Cloud functions that trigger DAGs based on GCS or Cloud Pub/Sub events, provisioning and configuring Cloud Router and Cloud NAT for downloading from PyPi/Maven/CRAN packages from the internet.

| # | Module | Link |
| -- | :---    | ---|
| 1 | ..| | 

### Module 4: Securing Cloud Composer 2 - iteration 2

This module adds VPC-SC and PSC to the setup in module 3.0.

| # | Module | Link |
| -- | :---    | ---|
| 1 | ..| | 


## Credits
This is a community contribution. <br>


| # | Contributor | Contribution | About |
| -- | :---    | :---| :---| 
| 1 | Anagha Khanolkar | Primary Author | Data Analytics Specialist, Google Cloud |
| 2 | Jay O' Leary | Testing, User experience | Data Analytics Specialist, Google Cloud |
