from fastapi import APIRouter, HTTPException
import pandas as pd

router = APIRouter(
  prefix="/api/v1",
  tags=["api/v1"],
)

@router.get('/')
def root():
  return {'message': 'Hello from score route'}

@router.get('/get_prediction', status_code=200)
async def send_data(year: str, month: str):
    if year == '' or month == '':
        raise HTTPException(status_code=404, detail="Send year and month")
        
    # Read from postgresql or other DB ... :D
    data = pd.read_csv('/opt/data/batch_predictions/predictions.csv')

    result = data[data.Periodo == f'{year}-{month}']
    if result.shape[0] == 0:
        raise HTTPException(status_code=500, detail="Invalid period")

    return {'prediction': result["preds"].values[0]} 
