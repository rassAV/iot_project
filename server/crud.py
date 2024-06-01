from sqlalchemy.orm import Session
import models
import schemas
import datetime

def get_pm25(db: Session, esp_name: str = 0):
    results = db.query(models.Data).filter(models.Data.esp_name == esp_name).all()
    return [i.pm25 for i in results]

def get_pm10(db: Session, esp_name: str = 0):
    results = db.query(models.Data).filter(models.Data.esp_name == esp_name).all()
    return [i.pm10 for i in results]

def get_esp_names(db: Session):
    return db.query(models.Clients.esp_name).all()

def create_data(db: Session, data: schemas.AirValue):
    db_data = models.Data(**{"pm25": data.pm25, "pm10": data.pm10, "esp_name": data.esp_name, "timestamp": datetime.datetime.now()})
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data
