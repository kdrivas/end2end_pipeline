"""
    This file contains the function for data gathering, merging and preprocessing
"""
import pandas as pd
from sklearn.pipeline import Pipeline
import os

from dags.pipelines.model_pipeline.constants import MERGE_COLS, MILK_COLS, BANK_COLS, PREP_COLS
from dags.pipelines.model_pipeline.constants import PIB_COLS, IMACEC_INDICE_COLS
from dags.pipelines.model_pipeline.constants import TARGET_COL

from dags.utils.transformers import FixingFormattedString, TakeVariables, RollingTransformer

def collect_milk_data(path: str, file_name: str) -> None:
    """
        This function will collect the data and create columns for the merge step
    """
    df = pd.read_csv(os.path.join(path, file_name))
    df.rename(columns = {'Anio': 'anio', 'Mes': 'mes'}, inplace = True)
    df['mes'] = pd.to_datetime(df['mes'], format = '%b')
    df['mes'] = df['mes'].apply(lambda x: x.month)

    df[MILK_COLS + [TARGET_COL]].to_csv(os.path.join(path, 'collect_' + file_name), index=False)

def collect_prep_data(path: str, file_name: str) -> None:
    """
        This function will collect the data and create columns for the merge step
    """
    df = pd.read_csv(os.path.join(path, file_name))
    df['date'] = pd.to_datetime(df['date'], format = '%Y-%m-%d')
    df[['mes', 'anio']] = df['date'].apply(lambda x: pd.Series([x.month, x.year]))

    df[PREP_COLS].to_csv(os.path.join(path, 'collect_' + file_name), index=False)

def collect_bank_data(path: str, file_name: str) -> None:
    """
        This function will collect the data and create columns for the merge step
    """
    df = pd.read_csv(os.path.join(path, file_name))

    df['Periodo'] = pd.to_datetime(df['Periodo'], infer_datetime_format=True, errors = 'coerce')
    df.drop_duplicates(subset = 'Periodo', inplace = True)
    df[['anio', 'mes']] = df['Periodo'].apply(lambda x: pd.Series([x.year, x.month]))

    df = df[BANK_COLS].dropna()

    df[BANK_COLS].to_csv(os.path.join(path, 'collect_' + file_name), index=False)

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

    # Shift variables
    # Shift operations won't be part of the production pipeline
    df_merge[MERGE_COLS] = df_merge[MERGE_COLS].shift(1)

    df_merge[MERGE_COLS + [TARGET_COL]].to_csv(os.path.join(path, 'merge_data.csv'), index=False)

def preprocess_data(path: str) -> None:
    """
        This function will execute the data preprocessing and serialize the data pipeline
    """

    pipe =  Pipeline([
        ('fixing_pib_vars', FixingFormattedString(PIB_COLS, 'PIB')),
        ('fixing_imacec_indice_vars', FixingFormattedString(IMACEC_INDICE_COLS, 'IMACEC_INDICE')),
        ('rolling_with_mean', RollingTransformer(MERGE_COLS, 'mean')),
        ('rolling_with_std', RollingTransformer(MERGE_COLS, 'std')),
    ])

    df_merge = pd.read_csv(os.path.join(path, 'merge_data.csv'))
    df_prec = pipe.fit_transform(df_merge)

    # df_merge[MERGE_COLS] = df_merge[MERGE_COLS].shift(1)

    df_prec.to_csv(os.path.join(path, 'preprocessed_data.csv'), index=False)
