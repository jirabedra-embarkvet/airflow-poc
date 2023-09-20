from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.amazon.aws.operators.batch import BatchOperator


AWS_BATCH_JOB_DEFINITION = AWS_BATCH_JOB_QUEUE = 'airflow-aws-batch-example'

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2015, 6, 1),
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
        dag_id='hello-batch',
        schedule=None,
        schedule_interval=None,
        default_args=default_args,
        max_active_runs=1,
) as dag:

    hello_world = BatchOperator(
        dag=dag,
        task_id='hello-batch',
        job_name='hello-batch',
        job_definition='airflow-poc-jd',
        job_queue='airflow-poc-jq',
        overrides={},
        max_retries=1,
        aws_conn_id='aws_embark',
        region_name='us-east-1'
    )

    hello_world
