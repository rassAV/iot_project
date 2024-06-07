from fastapi import Depends, FastAPI, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from datetime import timedelta
import hashlib
import uuid
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

ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

@app.get("/")
def greet(request: Request):
    auth_token = request.cookies.get("auth_token")
    if auth_token:
        return RedirectResponse(url="/sensor")
    return templates.TemplateResponse("index.html", {"request": request, "message": "Hello!!!"})

@app.post("/register")
def register(
    request: Request,
    esp_name: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    if password != confirm_password:
        return templates.TemplateResponse("index.html", {"request": request, "message": "Passwords do not match."})
    client = db.query(models.Clients).filter(models.Clients.esp_name == esp_name).first()
    if client:
        return templates.TemplateResponse("index.html", {"request": request, "message": "ESP name already registered."})
    name = db.query(models.Data).filter(models.Data.esp_name == esp_name).first()
    if name == None:
        return templates.TemplateResponse("index.html", {"request": request, "message": "ESP name isn't in data."})
    new_client = models.Clients(esp_name=esp_name, password=hash_password(password))
    db.add(new_client)
    db.commit()
    return templates.TemplateResponse("index.html", {"request": request, "message": "Registration successful. Please log in."})

@app.post("/login")
def login(
    request: Request,
    esp_name: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    client = db.query(models.Clients).filter(models.Clients.esp_name == esp_name).first()
    if not client or not verify_password(password, client.password):
        return templates.TemplateResponse("index.html", {"request": request, "message": "Invalid ESP name or password."})
    response = RedirectResponse(url="/sensor")
    response.set_cookie(key="auth_token", value=uuid.uuid4().hex, httponly=True, max_age=60*60*24)
    return response

@app.get("/sensor")
def sensor_page(request: Request):
    return templates.TemplateResponse("sensor.html", {"request": request})

@app.post("/sensor")
def sensor_page(request: Request):
    return templates.TemplateResponse("sensor.html", {"request": request})

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