"""
    This file contains the function for data gathering, merging and preprocessing
"""
import pandas as pd
import os

def collect_milk_data(path: str, file_name: str) -> None:
    """
        This function will collect the data and create columns for the merge step
    """
    df = pd.read_csv(os.path.join(path, file_name))
    df.rename(columns = {'Anio': 'anio', 'Mes': 'mes'}, inplace = True) 
    df['mes'] = pd.to_datetime(df['mes'], format = '%b')
    df['mes'] = df['mes'].apply(lambda x: x.month)

    df.to_csv(os.path.join(path, 'collect_' + file_name))

def collect_precipitation_data(path: str, file_name: str) -> None:
    """
        This function will collect the data and create columns for the merge step
    """
    df = pd.read_csv(os.path.join(path, file_name))
    df['date'] = pd.to_datetime(df['date'], format = '%Y-%m-%d')
    df[['mes', 'anio']] = df['date'].apply(lambda x: pd.Series([x.month, x.year]))

    df.to_csv(os.path.join(path, 'collect_' + file_name))

def collect_bank_data(path: str, file_name: str) -> None:
    """
        This function will collect the data and create columns for the merge step
    """
    df = pd.read_csv(os.path.join(path, file_name))

    df['Periodo'] = pd.to_datetime(df['Periodo'], infer_datetime_format=True, errors = 'coerce')
    df.drop_duplicates(subset = 'Periodo', inplace = True) 
    df[['anio', 'mes']] = df['Periodo'].apply(lambda x: pd.Series([x.year, x.month]))

    cols_imacec = [x for x in list(df.columns) if 'Imacec' in x] + ['Indice_de_ventas_comercio_real_no_durables_IVCM']
    cols_pib = [x for x in list(df.columns) if 'PIB' in x]
    df = df[['anio', 'mes'] + cols_pib + cols_imacec]
    df = df.dropna()

    df.to_csv(os.path.join(path, 'collect_' + file_name))

def merge_data(path: str) -> None:
    """
        This function will merge the data from 3 sources. Using the path, the function
        will read the data sources from the previous step
    """
    df_bank = pd.read_csv(os.path.join(path, 'collect_banco_central.csv'))
    df_milk = pd.read_csv(os.path.join(path, 'collect_precio_leche.csv'))
    df_prec = pd.read_csv(os.path.join(path, 'collect_precipitaciones.csv'))

    df_merge = pd.merge(df_milk, df_prec, on = ['mes', 'anio'], how = 'inner')
    df_merge = pd.merge(df_merge, df_bank, on = ['mes', 'anio'], how = 'inner')
    df_merge = df_merge.sort_values(by = ['anio', 'mes'], ascending = True).reset_index(drop=True)

    df_merge.to_csv(os.path.join(path, 'merge_data.csv'))
