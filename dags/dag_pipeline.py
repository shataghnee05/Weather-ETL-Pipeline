import sys
import os
sys.path.insert(0,"/opt/airflow")
import asyncio
from airflow.sdk import dag,task
from src.extract import extract_data
from src.transform import transform_data
from src.load import load_data
from datetime import datetime,timedelta

defaults = {
    "retries":4,
    "retry_delay" : timedelta(minutes=4) 
}
@dag(
    dag_id="weather_ETL",
    start_date=datetime(2026,5,26),
    schedule="0 */2 * * *",
    default_args=defaults,
    catchup=False
)
def weather_DAG():
    @task
    def extract():
        asyncio.run(extract_data())
    @task
    def transform():
        transform_data()
    @task
    def load():
        load_data()
    extract() >> transform() >> load()

dag = weather_DAG()