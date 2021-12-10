"""
    Training pipeline for milk model 
"""
import time
from datetime import datetime
from pprint import pprint
import pandas as pd

from airflow import DAG
from airflow.operators.python import PythonOperator

from dags.utils.config import VERSION
from dags.utils.transformers import *
from dags.pipelines.food_model.data import collect_milk_data, collect_prep_data, collect_bank_data
from dags.pipelines.food_model.data import merge_data, preprocess_data, validate_data
from dags.pipelines.food_model.model import training_model, validate_promote_model, hypertune_model
from dags.pipelines.food_model.constants import PARAM_GRID

import pandas as pd
import numpy as np
import locale
import os

locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
AIRFLOW_HOME = os.getenv('AIRFLOW_HOME')

with DAG(
    dag_id=f'training_food_model_v{VERSION}',
    schedule_interval=None,
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=['example'],
) as dag:
    
    ###############################
    ## Data Gathering 
    ###############################

    data_path = os.path.join(AIRFLOW_HOME, 'data')
    artifact_path = os.path.join(AIRFLOW_HOME, 'artifacts')

    gather_milk_step = PythonOperator(
        task_id=f'gather_milk',
        python_callable=collect_milk_data,
        op_kwargs={
            'path': data_path, 
            'file_name': 'precio_leche.csv'
        }
    )

    gather_bank_step = PythonOperator(
        task_id=f'gather_bank',
        python_callable=collect_bank_data,
        op_kwargs={
            'path': data_path, 
            'file_name': 'banco_central.csv'
        }
    )

    gather_prec_step = PythonOperator(
        task_id=f'gather_prec',
        python_callable=collect_prep_data,
        op_kwargs={
            'path': data_path, 
            'file_name': 'precipitaciones.csv'
        }
    )

    ###############################
    ###  Merging data 
    ###############################

    merge_data_step = PythonOperator(
        task_id=f'merge_data',
        python_callable=merge_data,
        op_kwargs={
            'path': data_path, 
        }
    )

    ###############################
    ###  Preprocessing data 
    ###############################

    preprocessing_step = PythonOperator(
        task_id=f'preprocess_data',
        python_callable=preprocess_data,
        op_kwargs={
            'data_path': data_path, 
            'artifact_path': artifact_path, 
        }
    )

    ###############################
    ###  Data validation 
    ###############################

    validation_step = PythonOperator(
        task_id=f'validate_data',
        python_callable=validate_data,
        op_kwargs={
            'path': data_path, 
        }
    )

    ###############################
    ###  Model building and hypterunning
    ############################### 

    hyptertune_step = PythonOperator(
        task_id=f'hypertune_model',
        python_callable=hypertune_model,
        op_kwargs={
            'data_path': data_path, 
            'artifact_path': artifact_path, 
        }
    )

    training_step = PythonOperator(
        task_id=f'training_model',
        python_callable=training_model,
        op_kwargs={
            'data_path': data_path, 
            'artifact_path': artifact_path, 
        }
    )

    ###############################
    ###  Model validation 
    ###############################

    promote_step = PythonOperator(
        task_id=f'validate_model',
        python_callable=validate_promote_model,
        op_kwargs={
            'data_path': data_path, 
            'artifact_path': artifact_path, 
        }
    )
    gather_milk_step >> merge_data_step
    gather_bank_step >> merge_data_step
    gather_prec_step >> merge_data_step

    merge_data_step >> preprocessing_step >> validation_step
    validation_step >> hyptertune_step >> training_step >> promote_step
