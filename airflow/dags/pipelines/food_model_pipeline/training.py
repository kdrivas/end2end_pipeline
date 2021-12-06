"""Example DAG demonstrating the usage of the PythonOperator."""
import time
from datetime import datetime
from pprint import pprint
import pandas as pd

from airflow import DAG
from airflow.operators.python import PythonOperator, PythonVirtualenvOperator

from dags.utils.config import VERSION
import pandas as pd
import numpy as np
import sys
import sklearn
import os

with DAG(
    dag_id=f'training_v{VERSION}',
    schedule_interval='None',
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

    def super_train():
        df_fall = pd.read_csv('./data/precipitaciones.csv')
        df_bank = pd.read_csv('./data/banco_central.csv')
        df_milk = pd.read_csv('./data/precio_leche.csv')
        
        df_fall['date'] = pd.to_datetime(df_fall['date'], format = '%Y-%m-%d')
        df_fall = df_fall.sort_values(by = 'date', ascending = True).reset_index(drop = True)
        
        df_bank['Periodo'] = df_bank['Periodo'].apply(lambda x: x[0:10])
        df_bank['Periodo'] = pd.to_datetime(df_bank['Periodo'], format = '%Y-%m-%d', errors = 'coerce')
        df_bank[df_bank.duplicated(subset = 'Periodo', keep = False)] #repetido se elimina

        df_bank.drop_duplicates(subset = 'Periodo', inplace = True)
        df_bank = df_bank[~df_bank.Periodo.isna()]

        def convert_int(x):
            return int(x.replace('.', ''))

        cols_pib = [x for x in list(df_bank.columns) if 'PIB' in x]
        cols_pib.extend(['Periodo'])
        df_bank_pib = df_bank[cols_pib]
        df_bank_pib = df_bank_pib.dropna(how = 'any', axis = 0)

        for col in cols_pib:
            if col == 'Periodo':
                continue
            else:
                df_bank_pib[col] = df_bank_pib[col].apply(lambda x: convert_int(x))

        df_bank_pib.sort_values(by = 'Periodo', ascending = True)

    def to_100(x): #mirando datos del bc, pib existe entre ~85-120 - igual esto es cm (?)
    x = x.split('.')
    if x[0].startswith('1'): #es 100+
        if len(x[0]) >2:
            return float(x[0] + '.' + x[1])
        else:
            x = x[0]+x[1]
            return float(x[0:3] + '.' + x[3:])
    else:
        if len(x[0])>2:
            return float(x[0][0:2] + '.' + x[0][-1])
        else:
            x = x[0] + x[1]
            return float(x[0:2] + '.' + x[2:])
        
    cols_imacec = [x for x in list(banco_central.columns) if 'Imacec' in x]
    cols_imacec.extend(['Periodo'])
    banco_central_imacec = banco_central[cols_imacec]
    banco_central_imacec = banco_central_imacec.dropna(how = 'any', axis = 0)

    for col in cols_imacec:
        if col == 'Periodo':
            continue
        else:
            banco_central_imacec[col] = banco_central_imacec[col].apply(lambda x: to_100(x))
            assert(banco_central_imacec[col].max()>100)
            assert(banco_central_imacec[col].min()>30)

    banco_central_imacec.sort_values(by = 'Periodo', ascending = True)
    banco_central_imacec

    run_this = PythonOperator(
        task_id='print_the_context',
        python_callable=print_context,
    )
    # [END howto_operator_python]

    # [START howto_operator_python_kwargs]
    def my_sleeping_function(random_base):
        """This is a function that will run within the DAG execution"""
        print(os.path.dirname(os.path.abspath(__file__)))
        time.sleep(random_base)

    # Generate 5 sleeping tasks, sleeping from 0.0 to 0.4 seconds respectively
    task = PythonOperator(
        task_id='sleep_for_' + str(i),
        python_callable=super_train,
        op_kwargs={'random_base': 10},
    )

    run_this >> task
    # [END howto_operator_python_kwargs]

    # [START howto_operator_python_venv]
    def callable_virtualenv():
        """
        Example function that will be performed in a virtual environment.

        Importing at the module level ensures that it will not attempt to import the
        library before it is installed.
        """
        from time import sleep

        from colorama import Back, Fore, Style

        print(Fore.RED + 'some red text')
        print(Back.GREEN + 'and with a green background')
        print(Style.DIM + 'and in dim text')
        print(Style.RESET_ALL)
        for _ in range(10):
            print(Style.DIM + 'Please wait...', flush=True)
            sleep(10)
        print('Finished')

    virtualenv_task = PythonVirtualenvOperator(
        task_id="virtualenv_python",
        python_callable=callable_virtualenv,
        requirements=["colorama==0.4.0"],
        system_site_packages=False,
    )
    # [END howto_operator_python_venv]
