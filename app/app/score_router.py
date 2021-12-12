from fastapi import APIRouter, HTTPException, Form
import pandas as pd
import joblib
from typing import Dict
from .utils import check_data_in_request
import logging

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
async def send_online_data(payload: Dict):
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

    return {'prediction': preds[-1]} 