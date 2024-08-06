from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

from src.extract import extract
from src.transform import transform
from src.load_to_gsheets import load_to_gsheets
from src.load_to_postgresql import load_to_postgresql

# Configurações padrão da DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 7, 30),
    'retries': 3,
    'retry_delay': timedelta(minutes=10),
}

# Criação da DAG
dag = DAG(
    'satisfacao_comunidade_dag',
    default_args=default_args,
    description='DAG para extrair, transformar e carregar dados de satisfação de membros da comunidade de código',
    schedule_interval='@daily',
    catchup=False
)

def extract_task():
    extract()

def transform_task(**context):
    df = transform()
    context['task_instance'].xcom_push(key='transformed_data', value=df)

def load_task_gsheets(**context):
    df = context['task_instance'].xcom_pull(task_ids='transform', key='transformed_data')
    load_to_gsheets(df)

def load_task_postgresql(**context):
    df = context['task_instance'].xcom_pull(task_ids='transform', key='transformed_data')
    load_to_postgresql(df)

# Tarefa de extração
extract_operator = PythonOperator(
    task_id='extract',
    python_callable=extract_task,
    dag=dag,
)

# Tarefa de transformação
transform_operator = PythonOperator(
    task_id='transform',
    python_callable=transform_task,
    dag=dag,
)

# Tarefa de carga para Google Sheets
load_gsheets_operator = PythonOperator(
    task_id='load_task_gsheets',
    python_callable=load_task_gsheets,
    dag=dag,
)

# Tarefa de carga para PostgreSQL
load_postgresql_operator = PythonOperator(
    task_id='load_task_postgresql',
    python_callable=load_task_postgresql,
    dag=dag,
)

# Define a ordem de execução das tarefas
extract_operator >> transform_operator >> [load_gsheets_operator, load_postgresql_operator]
