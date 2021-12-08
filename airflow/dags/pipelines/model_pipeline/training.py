"""Example DAG demonstrating the usage of the PythonOperator."""
import time
from datetime import datetime
from pprint import pprint
import pandas as pd

from airflow import DAG
from airflow.operators.python import PythonOperator, PythonVirtualenvOperator

from dags.utils.config import VERSION
from dags.utils.transformers import *
from dags.pipelines.model_pipeline.data import collect_milk_data, collect_prep_data, collect_bank_data
from dags.pipelines.model_pipeline.data import merge_data

import pandas as pd
import numpy as np
import locale
import sys
import sklearn
import os

locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
AIRFLOW_HOME = os.getenv('AIRFLOW_HOME')

with DAG(
    dag_id=f'training_v{VERSION}',
    schedule_interval=None,
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=['example'],
) as dag:
    # [START howto_operator_python]
    def print_context(ds, **kwargs):
        """Print the Airflow context and ds variable from the context."""
        pprint(kwargs)
        print(ds)
        return 'Whatever you return gets printed in the logs'

    ###############################
    ## Data Gathering 
    ###############################

    base_path = os.path.join(AIRFLOW_HOME, 'airflow/dags/pipelines/model_pipeline/')

    gather_milk_step = PythonOperator(
        task_id=f'gather_milk_v{VERSION}',
        python_callable=collect_milk_data,
        op_kwargs={
            'path': 'base_path', 
            'file_name': 'precio_leche.csv'
        }
    )

    gather_bank_step = PythonOperator(
        task_id=f'gather_bank_v{VERSION}',
        python_callable=collect_bank_data,
        op_kwargs={
            'path': 'base_path', 
            'file_name': 'banco_central.csv'
        }
    )

    gather_prec_step = PythonOperator(
        task_id=f'gather_prec_v{VERSION}',
        python_callable=collect_prep_data,
        op_kwargs={
            'path': 'base_path', 
            'file_name': 'precipitaciones.csv'
        }
    )

    ###############################
    ###  Merging data 
    ###############################

    merge_data_step = PythonOperator(
        task_id='merge_data_v{VERSION}',
        python_callable=merge_data,
    )

    gather_milk_step >> merge_data_step
    gather_bank_step >> merge_data_step
    gather_prec_step >> merge_data_step
