from datetime import datetime, timedelta
import datetime as dt
from airflow import DAG
from airflow.operators.empty import EmptyOperator

with DAG(
        dag_id='hello-empty-operator',
        schedule=None,
        schedule_interval=None,
        max_active_runs=1,
        start_date=dt.datetime(2023, 9, 20),
        catchup=False
) as dag:

    hello_batch = EmptyOperator(
        dag=dag,
        task_id='hello_batch',
    )

    hello_batch
