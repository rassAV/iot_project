from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import datetime
import schemas
import models
import crud

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(schemas.router)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def greet():
    return {"Message": "Hello!!!"}

@app.get("/air/{esp_name}")
def get_air(esp_name: str, db: Session = Depends(get_db)):
    db_data = crud.get_data(db, esp_name=esp_name)
    if db_data is None:
        raise HTTPException(status_code=404, detail="data not found")
    return {"values": db_data}

@app.post("/submit_air")
def submit_air(
    measurement: schemas.AirValue,
    db: Session = Depends(get_db)
):
    return crud.create_data(db=db, data=measurement)
