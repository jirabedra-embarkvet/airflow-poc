from airflow import DAG
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow import task
from datetime import timedelta
import datetime as dt

# define the python function
def my_function(x):
    return x + " is a must have tool for Data Engineers."

dag = DAG(
    'python_operator_sample',
    description='How to use the Python Operator?',
    schedule_interval=timedelta(days=1),
    start_date=dt('2023-9-9')
)

t1 = PythonOperator(
    task_id='print',
    python_callable= my_function,
    op_kwargs = {"x" : "Apache Airflow"},
    dag=dag,
)


t1