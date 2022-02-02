"""Example Airflow DAG that creates a Cloud Dataflow workflow which takes a
text file and adds the rows to a BigQuery table.

This DAG relies on six Airflow variables
https://airflow.apache.org/docs/apache-airflow/stable/concepts/variables.html
* project_id - Google Cloud Project ID to use for the Cloud Dataflow cluster.
* source_file_bucket_path - where the source files are available
* dataflow_subnet - for specific subnet for Dataflow pipeline that gets provisioned
* umsa_fqn - the fully qualified user managed service account name to run the DAG as
* bq_ds - the BQ dataset hosting the tables to load data into
* bq_tbl_nm - the BQ table to load data into

It uses the DataflowTemplatedJobStartOperator specifically with a template at
gs://dataflow-templates/latest/GCS_Text_to_BigQuery
and reads text files in GCS, maps and/or transforms data in files to BQ, and
loads a BQ table provided as parameter

This template takes 5 parameters as show in the "start_template_job", "parameters"
"""

import datetime

from airflow import models
from airflow.providers.google.cloud.operators.dataflow import DataflowTemplatedJobStartOperator
from airflow.utils.dates import days_ago


project_id = models.Variable.get("project_id")
source_file_bucket_path = models.Variable.get("source_file_bucket_path")
dataflow_subnet = models.Variable.get("dataflow_subnet")
umsa_fqn = models.Variable.get("umsa_fqn")
bq_ds = models.Variable.get("bq_ds")
bq_tbl_nm = models.Variable.get("bq_tbl_nm")
use_public_ips_in_dataflow = models.Variable.get("use_public_ips_in_dataflow")


default_args = {
    # Tell airflow to start one day ago, so that it runs as soon as you upload it
    "start_date": days_ago(1),
    "dataflow_default_options": {
        "project": project_id,
        "tempLocation": source_file_bucket_path + "/tmp/", # Scratch dir
        "subnetwork": dataflow_subnet, # Deply in BYO Subnet
        "serviceAccountEmail": umsa_fqn, # Run DAG as UMSA
        "usePublicIps": use_public_ips_in_dataflow
    },
}

# Define a DAG (directed acyclic graph) of tasks.
# Any task you create within the context manager is automatically added to the
# DAG object.
with models.DAG(
    # The id you will see in the DAG airflow page
    "ultra_basic_gcs_cdf_bq_dag",
    default_args=default_args,
    # The interval with which to schedule the DAG
    schedule_interval=datetime.timedelta(days=1),  # Override to match your needs
) as dag:

    start_template_job = DataflowTemplatedJobStartOperator(
        # The task id of your job
        task_id="dataflow_operator_transform_csv_to_bq",
        # The name of the template that you're using.
        # Below is a list of all the templates you can use.
        # For versions in non-production environments, use the subfolder 'latest'
        # https://cloud.google.com/dataflow/docs/guides/templates/provided-batch#gcstexttobigquery
        template="gs://dataflow-templates/latest/GCS_Text_to_BigQuery",
        # Use the link above to specify the correct parameters for your template.
        parameters={
            "javascriptTextTransformFunctionName": "transformCSVtoJSON",
            "JSONPath": source_file_bucket_path + "/jsonSchema.json",
            "javascriptTextTransformGcsPath": source_file_bucket_path + "/transformCSVtoJSON.js",
            "inputFilePattern": source_file_bucket_path + "/inputFile.txt",
            "outputTable": project_id + ":" + bq_ds + "." + bq_tbl_nm,
            "bigQueryLoadingTemporaryDirectory": source_file_bucket_path + "/tmp/"
        },
    )