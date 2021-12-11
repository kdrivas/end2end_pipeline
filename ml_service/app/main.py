from fastapi import FastAPI, status
from app import score_router
import logging

app = FastAPI()

logging.config.fileConfig('log.config', disable_existing_loggers=False)

app.include_router(score_router.router)

@app.get('/check_service', status_code=status.HTTP_201_CREATED)
def root():
  return {'Message': 'Hello world from service'}