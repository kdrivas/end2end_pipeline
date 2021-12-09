"""
    This file contains the function for data gathering, merging and preprocessing
"""
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.feature_selection import SelectKBest, mutual_info_regression
import os
import joblib

from dags.pipelines.model_pipeline.constants import MERGE_COLS, MILK_COLS, BANK_COLS, PREP_COLS
from dags.pipelines.model_pipeline.constants import CITY_COLS, PIB_COLS, IMACEC_INDICE_COLS, TAKE_VARS
from dags.pipelines.model_pipeline.constants import TARGET_COL

from dags.utils.transformers import FixingFormattedString, DropNaTransformer, TakeVariables, RollingTransformer

def collect_milk_data(path: str, file_name: str) -> None:
    """
        This function will collect the data and create columns for the merge step
    """
    df = pd.read_csv(os.path.join(path, 'raw', file_name))
    df.rename(columns = {'Anio': 'anio', 'Mes': 'mes'}, inplace = True)
    df['mes'] = pd.to_datetime(df['mes'], format = '%b')
    df['mes'] = df['mes'].apply(lambda x: x.month)

    df[MILK_COLS].to_csv(os.path.join(path, 'interm', 'collect_' + file_name), index=False)

def collect_prep_data(path: str, file_name: str) -> None:
    """
        This function will collect the data and create columns for the merge step
    """
    df = pd.read_csv(os.path.join(path, 'raw', file_name))
    df['date'] = pd.to_datetime(df['date'], format = '%Y-%m-%d')
    df[['mes', 'anio']] = df['date'].apply(lambda x: pd.Series([x.month, x.year]))

    df[PREP_COLS].to_csv(os.path.join(path,'interm',  'collect_' + file_name), index=False)

def collect_bank_data(path: str, file_name: str) -> None:
    """
        This function will collect the data and create columns for the merge step
    """
    df = pd.read_csv(os.path.join(path, 'raw', file_name))

    df['Periodo'] = pd.to_datetime(df['Periodo'], infer_datetime_format=True, errors = 'coerce')
    df.drop_duplicates(subset = 'Periodo', inplace = True)
    df[['anio', 'mes']] = df['Periodo'].apply(lambda x: pd.Series([x.year, x.month]))

    df = df[BANK_COLS].dropna()

    df[BANK_COLS].to_csv(os.path.join(path, 'interm', 'collect_' + file_name), index=False)

def merge_data(path: str) -> None:
    """
        This function will merge the data from 3 sources. Using the path, the function
        will read the data sources from the previous step
    """
    df_bank = pd.read_csv(os.path.join(path, 'interm', 'collect_banco_central.csv'))
    df_milk = pd.read_csv(os.path.join(path, 'interm', 'collect_precio_leche.csv'))
    df_prec = pd.read_csv(os.path.join(path, 'interm', 'collect_precipitaciones.csv'))

    df_merge = pd.merge(df_milk, df_prec, on = ['mes', 'anio'], how = 'inner')
    df_merge = pd.merge(df_merge, df_bank, on = ['mes', 'anio'], how = 'inner')
    df_merge = df_merge.sort_values(by = ['anio', 'mes'], ascending = True).reset_index(drop=True)

    # Shift variables
    # Shift operations won't be part of the production pipeline
    df_merge[TARGET_COL] = df_merge['Precio_leche']
    df_merge[MERGE_COLS] = df_merge[MERGE_COLS].shift(1)

    df_merge[MERGE_COLS + [TARGET_COL]].dropna().to_csv(os.path.join(path, 'interm', 'merge_data.csv'), index=False)

def preprocess_data(data_path: str, artifact_path: str) -> None:
    """
        This function will execute the data preprocessing and serialize the data pipeline
    """

    # The pipeline is divided in two parts due to the presence of null values

    pipe_1 =  Pipeline([
        ('fixing_pib_vars', FixingFormattedString(PIB_COLS, 'PIB')),
        ('fixing_imacec_indice_vars', FixingFormattedString(IMACEC_INDICE_COLS, 'IMACEC_INDICE')),
        ('rolling_with_mean', RollingTransformer(['Precio_leche'] + CITY_COLS + PIB_COLS + IMACEC_INDICE_COLS, 'mean')),
        ('rolling_with_std', RollingTransformer(['Precio_leche'] + CITY_COLS + PIB_COLS + IMACEC_INDICE_COLS, 'std')),
        ('take_vars_before_scaler', TakeVariables([TARGET_COL] + TAKE_VARS)),
    ])

    pipe_2 =  Pipeline([
        ('scale', StandardScaler()),
        ('selector', SelectKBest(mutual_info_regression)),
        ('polynomial_features', PolynomialFeatures()),
    ])

    # Read the data and set the period as index
    df_merge = pd.read_csv(os.path.join(data_path, 'interm', 'merge_data.csv'))
    df_merge['Periodo'] = df_merge.apply(lambda x: str(int(x.anio)) + '-' + str(int(x.mes)), axis=1)
    df_merge.set_index('Periodo', inplace=True)

    # Apply the first step of the preprocessing and remove nan
    # TO-DO: Improve this hardcoding steps
    df_interm = pipe_1.fit_transform(df_merge)
    df_interm = df_interm.dropna()

    df_interm_X_train, df_interm_X_test, df_interm_y_train, df_interm_y_test = train_test_split(df_interm.drop(TARGET_COL, axis=1), df_interm[TARGET_COL], test_size=0.2, random_state=42)

    # Apply the second step of the preprocessing
    df_prec_X_train = pipe_2.fit_transform(df_interm_X_train, df_interm_y_train)
    df_prec_X_test = pipe_2.transform(df_interm_X_test)

    df_prec_train = pd.concat((df_interm_y_train.reset_index(drop=True), pd.DataFrame(df_prec_X_train)), axis=1)
    df_prec_test = pd.concat((df_interm_y_test.reset_index(drop=True), pd.DataFrame(df_prec_X_test)), axis=1)

    # Apply the preprocessing using all the data
    df_prec_all_raw = pipe_2.transform(df_interm.drop(TARGET_COL, axis=1))
    df_prec_all = pd.concat((df_interm[TARGET_COL], pd.DataFrame(df_prec_all_raw)), axis=1)

    # Saving data and serializing pipelines
    df_prec_train.to_csv(os.path.join(data_path, 'preprocessed', 'train.csv'), index=False)
    df_prec_test.to_csv(os.path.join(data_path, 'preprocessed', 'test.csv'), index=False)
    
    # TO-DO: Use Feast!!!
    df_prec_all.to_csv(os.path.join(data_path, 'feature_store', 'super_efficient_feature_store.csv'), index=False)

    joblib.dump(pipe_1, os.path.join(artifact_path, 'pipe_1.pkl'))
    joblib.dump(pipe_2, os.path.join(artifact_path, 'pipe_2.pkl'))

def validate_data(path: str) -> None:
    """
        This function have a small set of validations to be sure the preprocessed data
        is correct
    """
    data = pd.read_csv(os.path.join(path, 'preprocessed', 'train.csv'))

    assert data.shape[0] > 0
    assert data.shape[1] == 67
