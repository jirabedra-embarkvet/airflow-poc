# To initiate the DAG Object
from airflow import DAG
# Importing datetime and timedelta modules for scheduling the DAGs
from datetime import timedelta, datetime
# Importing operators 
from airflow.operators.empty import EmptyOperator

# Initiating the default_args
default_args = {
        'owner' : 'airflow',
        'start_date' : datetime(2023, 9, 9)
}

# Creating DAG Object
dag = DAG(dag_id='hello-world-juan',
        default_args=default_args,
        schedule='@once', 
        catchup=False
    )

 # Creating first task
start = EmptyOperator(task_id
  = 'start', dag = dag)

# Creating second task
end = EmptyOperator(task_id 
= 'end', dag = dag)

# Setting up dependencies 
start >> end 
# We can also write it as start.set_downstream(end)