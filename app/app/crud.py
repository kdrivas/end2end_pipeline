from sqlalchemy.orm import Session

from . import models
from . import schemas

def create_record(db: Session, item: schemas.PredictionCreate):
    db_item = models.Prediction(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
  
    return db_item

def get_record(db: Session, limit: int = 100):
    return db.query(models.Prediction).limit(100).all()