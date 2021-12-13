from fastapi import APIRouter, HTTPException, Depends
import pandas as pd
import joblib
import logging
from typing import Dict
import random

from .utils import check_data_in_request
from .crud import create_record
from .schemas import PredictionCreate
from .deps import get_session

valid_columns = pd.read_csv('/opt/data/interm/merge_data.csv').columns.tolist()
valid_columns.remove('target')
model_pipe = joblib.load('/opt/artifacts/model_prod.pkl')
data_pipe = joblib.load('/opt/artifacts/data_pipeline.pkl')

router = APIRouter(
  prefix="/api/v1",
  tags=["api/v1"],
)

@router.get('/')
def root():
  return {'message': 'Hello from score route'}

@router.get('/get_prediction', status_code=200)
async def send_data(year: str, month: str):
    """
        Get the prediction for a specific period of time
    """
    if year == '' or month == '':
        raise HTTPException(status_code=500, detail="Send year and month")
        
    # Read from postgresql or other DB ... :D
    data = pd.read_csv('/opt/data/batch_predictions/predictions.csv')

    result = data[data.Periodo == f'{year}-{month}']
    if result.shape[0] == 0:
        raise HTTPException(status_code=500, detail="Invalid period")

    return {'prediction': result["preds"].values[0]} 

@router.post('/get_online_prediction', status_code=200)
async def send_online_data(payload: Dict, db = Depends(get_session)):
    """
        Get the prediction for the requested data
        Input:
            data: The data from three periods before the period you want to predict
            data: Dict=Form(...)
    """
    data = payload["data"]
    if not check_data_in_request(data, valid_columns):
        raise HTTPException(status_code=500, detail="Invalid data")
        
    data = pd.DataFrame(data)
    data_prec = data_pipe.transform(data)
    data_prec = data_prec.dropna()
    preds = model_pipe.predict(data_prec)

    # TO-DO: Create other unique ID
    dummyUniqueID = random.randint(0,1000000)

    # TO-DO: Refactor
    for _, record_to_DB in data.iterrows():
        item = PredictionCreate(
            dummyUniqueID = dummyUniqueID,
            anio = record_to_DB['anio'],
            mes = record_to_DB['mes'],
            Precio_leche = record_to_DB['Precio_leche'],
            Coquimbo = record_to_DB['Coquimbo'],
            Valparaiso = record_to_DB['Valparaiso'],
            Metropolitana_de_Santiago = record_to_DB['Metropolitana_de_Santiago'],
            Maule = record_to_DB['Maule'],
            Biobio = record_to_DB['Biobio'],
            La_Araucania = record_to_DB['La_Araucania'],
            Los_Rios = record_to_DB['Los_Rios'],
            PIB_Agropecuario_silvicola = record_to_DB['PIB_Agropecuario_silvicola'],
            PIB_Pesca = record_to_DB['PIB_Pesca'],
            PIB_Mineria = record_to_DB['PIB_Mineria'],
            PIB_Mineria_del_cobre = record_to_DB['PIB_Mineria_del_cobre'],
            PIB_Otras_actividades_mineras = record_to_DB['PIB_Otras_actividades_mineras'],
            PIB_Industria_Manufacturera = record_to_DB['PIB_Industria_Manufacturera'],
            PIB_Alimentos = record_to_DB['PIB_Alimentos'],
            PIB_Bebidas_y_tabaco = record_to_DB['PIB_Bebidas_y_tabaco'],
            PIB_Textil = record_to_DB['PIB_Textil'],
            PIB_Maderas_y_muebles = record_to_DB['PIB_Maderas_y_muebles'],
            PIB_Celulosa = record_to_DB['PIB_Celulosa'],
            PIB_Refinacion_de_petroleo = record_to_DB['PIB_Refinacion_de_petroleo'],
            PIB_Minerales_no_metalicos_y_metalica_basica = record_to_DB['PIB_Minerales_no_metalicos_y_metalica_basica'],
            PIB_Productos_metalicos = record_to_DB['PIB_Productos_metalicos'],
            PIB_Electricidad = record_to_DB['PIB_Electricidad'],
            PIB_Construccion = record_to_DB['PIB_Construccion'],
            PIB_Comercio = record_to_DB['PIB_Comercio'],
            PIB_Restaurantes_y_hoteles = record_to_DB['PIB_Restaurantes_y_hoteles'],
            PIB_Transporte = record_to_DB['PIB_Transporte'],
            PIB_Comunicaciones = record_to_DB['PIB_Comunicaciones'],
            PIB_Servicios_financieros = record_to_DB['PIB_Servicios_financieros'],
            PIB_Servicios_empresariales = record_to_DB['PIB_Servicios_empresariales'],
            PIB_Servicios_de_vivienda = record_to_DB['PIB_Servicios_de_vivienda'],
            PIB_Servicios_personales = record_to_DB['PIB_Servicios_personales'],
            PIB_Administracion_publica = record_to_DB['PIB_Administracion_publica'],
            PIB_a_costo_de_factores = record_to_DB['PIB_a_costo_de_factores'],
            PIB = record_to_DB['PIB'],
            Imacec_empalmado = record_to_DB['Imacec_empalmado'],
            Imacec_produccion_de_bienes = record_to_DB['Imacec_produccion_de_bienes'],
            Imacec_minero = record_to_DB['Imacec_minero'],
            Imacec_industria = record_to_DB['Imacec_industria'],
            Imacec_resto_de_bienes = record_to_DB['Imacec_resto_de_bienes'],
            Imacec_comercio = record_to_DB['Imacec_comercio'],
            Imacec_servicios = record_to_DB['Imacec_servicios'],
            Imacec_a_costo_de_factores = record_to_DB['Imacec_a_costo_de_factores'],
            Imacec_no_minero = record_to_DB['Imacec_no_minero'],
            Indice_de_ventas_comercio_real_no_durables_IVCM = record_to_DB['Indice_de_ventas_comercio_real_no_durables_IVCM'],
            pred = preds[-1]
        )
    
        new_item = create_record(db, item)

    return {'prediction': preds[-1]} 