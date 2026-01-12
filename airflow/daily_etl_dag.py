from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator


with DAG(
    dag_id="daily_restaurant_etl",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@daily",
    catchup=False,
) as dag:
    run_pipeline = BashOperator(
        task_id="run_pipeline",
        bash_command="python -m src.pipeline",
    )

