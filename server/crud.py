from sqlalchemy.orm import Session
import models
import schemas
import datetime

def get_data(db: Session, esp_name: str = 0):
    results = db.query(models.Data).filter(models.Data.esp_name == esp_name).all()
    return [i.pm25 for i in results]

def create_data(db: Session, data: schemas.AirValue):
    db_data = models.Data(**{"pm25": data.pm25, "pm10": data.pm10, "esp_name": data.esp_name, "timestamp": datetime.datetime.now()})
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data
