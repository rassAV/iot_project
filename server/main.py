from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import datetime
import schemas
import models
import crud

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(schemas.router)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def greet(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "message": "Hello!!!"})

@app.get("/pm25/{esp_name}")
def get_all_pm25(esp_name: str, db: Session = Depends(get_db)):
    db_data = crud.get_pm25(db, esp_name=esp_name)
    if not db_data:
        raise HTTPException(status_code=404, detail="data not found")
    return db_data

@app.get("/pm10/{esp_name}")
def get_all_pm10(esp_name: str, db: Session = Depends(get_db)):
    db_data = crud.get_pm10(db, esp_name=esp_name)
    if not db_data:
        raise HTTPException(status_code=404, detail="data not found")
    return db_data

@app.get("/esp_names", response_model=list[str])
def get_all_esp_names(db: Session = Depends(get_db)):
    esp_names = crud.get_esp_names(db)
    return [esp_name[0] for esp_name in esp_names]

@app.post("/submit_air")
def submit_air(
    measurement: schemas.AirValue,
    db: Session = Depends(get_db)
):
    return crud.create_data(db=db, data=measurement)
