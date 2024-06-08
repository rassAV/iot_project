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

def get_data_for_period(db: Session, esp_name: str, start_time: datetime.datetime = None, end_time: datetime.datetime = None):
    query = db.query(models.Data).filter(models.Data.esp_name == esp_name)
    if start_time:
        query = query.filter(models.Data.timestamp >= start_time)
    if end_time:
        query = query.filter(models.Data.timestamp <= end_time)
    return query.all()

def get_last_n_data(db: Session, esp_name: str, n: int):
    return db.query(models.Data).filter(models.Data.esp_name == esp_name).order_by(models.Data.timestamp.desc()).limit(n).all()