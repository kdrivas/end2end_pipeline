"""Example DAG demonstrating the usage of the PythonOperator."""
import time
from datetime import datetime
from pprint import pprint
import pandas as pd

from airflow import DAG
from airflow.operators.python import PythonOperator, PythonVirtualenvOperator

from dags.utils.config import VERSION
from dags.utils.transformers import *
from dags.pipelines.model_pipeline.data import collect_milk_data

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
    df = pd.read_csv(AIRFLOW_HOME + '/dags/pipelines/food_model_pipeline/precipitaciones.csv')#[mm]


    def super_train():
        precipitaciones = pd.read_csv(AIRFLOW_HOME + '/dags/pipelines/model_pipeline/precipitaciones.csv')#[mm]
        precio_leche = pd.read_csv(AIRFLOW_HOME + '/dags/pipelines/model_pipeline/precio_leche.csv')#[mm]
        banco_central = pd.read_csv(AIRFLOW_HOME + '/dags/pipelines/model_pipeline/banco_central.csv')#[mm]
        
        precipitaciones['date'] = pd.to_datetime(precipitaciones['date'], format = '%Y-%m-%d')
        precipitaciones = precipitaciones.sort_values(by = 'date', ascending = True).reset_index(drop = True)

        banco_central['Periodo'] = banco_central['Periodo'].apply(lambda x: x[0:10])

        banco_central['Periodo'] = pd.to_datetime(banco_central['Periodo'], format = '%Y-%m-%d', errors = 'coerce')

        banco_central.drop_duplicates(subset = 'Periodo', inplace = True)
        banco_central = banco_central[~banco_central.Periodo.isna()]

        def convert_int(x):
            return int(x.replace('.', ''))

        cols_pib = [x for x in list(banco_central.columns) if 'PIB' in x]
        cols_pib.extend(['Periodo'])
        banco_central_pib = banco_central[cols_pib]
        banco_central_pib = banco_central_pib.dropna(how = 'any', axis = 0)

        for col in cols_pib:
            if col == 'Periodo':
                continue
            else:
                banco_central_pib[col] = banco_central_pib[col].apply(lambda x: convert_int(x))

        banco_central_pib.sort_values(by = 'Periodo', ascending = True)

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

        banco_central_iv = banco_central[['Indice_de_ventas_comercio_real_no_durables_IVCM', 'Periodo']]
        banco_central_iv = banco_central_iv.dropna() # -unidades? #parte 
        banco_central_iv = banco_central_iv.sort_values(by = 'Periodo', ascending = True)

        banco_central_iv['num'] = banco_central_iv.Indice_de_ventas_comercio_real_no_durables_IVCM.apply(lambda x: to_100(x))
        banco_central_iv

        banco_central_num = pd.merge(banco_central_pib, banco_central_imacec, on = 'Periodo', how = 'inner')
        banco_central_num = pd.merge(banco_central_num, banco_central_iv, on = 'Periodo', how = 'inner')

        precio_leche.rename(columns = {'Anio': 'ano', 'Mes': 'mes_pal'}, inplace = True) # precio = nominal, sin iva en clp/litro
        precio_leche['mes'] = pd.to_datetime(precio_leche['mes_pal'], format = '%b')
        precio_leche['mes'] = precio_leche['mes'].apply(lambda x: x.month)
        precio_leche['mes-ano'] = precio_leche.apply(lambda x: f'{x.mes}-{x.ano}', axis = 1)

        precipitaciones['mes'] = precipitaciones.date.apply(lambda x: x.month)
        precipitaciones['ano'] = precipitaciones.date.apply(lambda x: x.year)
        precio_leche_pp = pd.merge(precio_leche, precipitaciones, on = ['mes', 'ano'], how = 'inner')
        precio_leche_pp.drop('date', axis = 1, inplace = True)
        precio_leche_pp #precipitaciones fecha_max = 2020-04-01

        banco_central_num['mes'] = banco_central_num['Periodo'].apply(lambda x: x.month)
        banco_central_num['ano'] = banco_central_num['Periodo'].apply(lambda x: x.year)
        precio_leche_pp_pib = pd.merge(precio_leche_pp, banco_central_num, on = ['mes', 'ano'], how = 'inner')
        precio_leche_pp_pib.drop(['Periodo', 'Indice_de_ventas_comercio_real_no_durables_IVCM', 'mes-ano', 'mes_pal'], axis =1, inplace = True)
        precio_leche_pp_pib

        cc_cols = [x for x in precio_leche_pp_pib.columns if x not in ['ano', 'mes']]

        precio_leche_pp_pib_shift3_mean = precio_leche_pp_pib[cc_cols].rolling(window=3, min_periods=1).mean().shift(1)

        precio_leche_pp_pib_shift3_mean.columns = [x+'_shift3_mean' for x in precio_leche_pp_pib_shift3_mean.columns]
                                                        
        precio_leche_pp_pib_shift3_std = precio_leche_pp_pib[cc_cols].rolling(window=3, min_periods=1).std().shift(1)

        precio_leche_pp_pib_shift3_std.columns = [x+'_shift3_std' for x in precio_leche_pp_pib_shift3_std.columns] 

        precio_leche_pp_pib_shift1 = precio_leche_pp_pib[cc_cols].shift(1)

        precio_leche_pp_pib_shift1.columns = [x+'_mes_anterior' for x in precio_leche_pp_pib_shift1.columns]

        precio_leche_pp_pib = pd.concat([precio_leche_pp_pib['Precio_leche'], precio_leche_pp_pib_shift3_mean, precio_leche_pp_pib_shift3_std, precio_leche_pp_pib_shift1], axis = 1) 
        precio_leche_pp_pib = precio_leche_pp_pib.dropna(how = 'any', axis = 0)
        precio_leche_pp_pib.head()

        X = precio_leche_pp_pib.drop(['Precio_leche'], axis = 1)
        y = precio_leche_pp_pib['Precio_leche']

        print('shape X', X.shape)
        print('shape y', y.shape)


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
        task_id='big_train',
        python_callable=super_train,
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
