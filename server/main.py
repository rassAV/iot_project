from fastapi import Depends, FastAPI, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, Response
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from datetime import datetime, timedelta
import hashlib
import uuid
import schemas
import models
import crud
import plotly.graph_objects as go
from statistics import mean, stdev

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

def verify_password_ho_hashed(plain_password: str, old_password: str) -> bool:
    return plain_password == old_password

@app.get("/")
def greet(request: Request):
    auth_token = request.cookies.get("esp_name")
    if auth_token:
        return RedirectResponse(url="/sensor")
    return templates.TemplateResponse("index.html", {"request": request, "message": "Hello!!!"})

@app.post("/change_password")
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
    new_client = models.Clients(esp_name=esp_name, password=password)
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
    if not client or not verify_password_ho_hashed(password, client.password):
        return templates.TemplateResponse("index.html", {"request": request, "message": "Invalid ESP name or password."})
    response = RedirectResponse(url="/sensor")
    response.set_cookie(key="esp_name", value=esp_name, httponly=True, max_age=60*60*24)
    return response

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

@app.get("/sensor")
def sensor_page(request: Request, db: Session = Depends(get_db)):
    auth_token = request.cookies.get("esp_name")
    if not auth_token:
        return RedirectResponse(url="/")
    client = db.query(models.Clients).filter(models.Clients.esp_name == auth_token).first()
    if not client:
        return RedirectResponse(url="/")
    
    esp_name = client.esp_name

    all_time_data = crud.get_data_for_period(db, esp_name)
    
    pm25_values = [data.pm25 for data in all_time_data]
    pm10_values = [data.pm10 for data in all_time_data]
    mean_pm25 = mean(pm25_values)
    mean_pm10 = mean(pm10_values)
    
    anomalies = []
    for data in all_time_data:
        if data.pm25 - mean_pm25 > 3 * stdev(pm25_values) or data.pm10 - mean_pm10 > 3 * stdev(pm10_values):
            anomalies.append(data)
    anomalies = anomalies[-5:]
    
    time_intervals = {
        "All Time": (datetime.now() - timedelta(days=365*10), datetime.now()),
        "Last Year": (datetime.now() - timedelta(days=365), datetime.now()),
        "Last Month": (datetime.now() - timedelta(days=30), datetime.now())
    }
    
    start_date, end_date = time_intervals["All Time"]
    
    interval_data = crud.get_data_for_period(db, esp_name, start_date, end_date)
    interval_dates = [data.timestamp for data in interval_data]
    interval_pm25 = [data.pm25 for data in interval_data]
    interval_pm10 = [data.pm10 for data in interval_data]
    
    last_5_data = crud.get_last_n_data(db, esp_name, n=5)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=interval_dates, y=interval_pm25, mode='lines', name='PM2.5', line=dict(color="black")))
    fig.add_trace(go.Scatter(x=interval_dates, y=interval_pm10, mode='lines', name='PM10', line=dict(color="gray")))
    
    fig.add_shape(
        dict(type="line", x0=min(interval_dates), y0=25, x1=max(interval_dates), y1=25, line=dict(color="yellow", width=5))
    )
    fig.add_shape(
        dict(type="line", x0=min(interval_dates), y0=50, x1=max(interval_dates), y1=50, line=dict(color="red", width=5))
    )
    
    fig.update_layout(title='Sensor Data', xaxis_title='Date', yaxis_title='Value')
    graph_html = fig.to_html(full_html=False, default_height=500, default_width=700)
    
    return templates.TemplateResponse("sensor.html", {"request": request, "graph": graph_html, "last_5_data": last_5_data, "mean_pm25": mean_pm25, "mean_pm10": mean_pm10, "anomalies": anomalies})

@app.post("/sensor")
def sensor_page(request: Request, db: Session = Depends(get_db)):
    auth_token = request.cookies.get("esp_name")
    if not auth_token:
        return RedirectResponse(url="/")
    client = db.query(models.Clients).filter(models.Clients.esp_name == auth_token).first()
    if not client:
        return RedirectResponse(url="/")
    
    esp_name = client.esp_name

    all_time_data = crud.get_data_for_period(db, esp_name)
    
    pm25_values = [data.pm25 for data in all_time_data]
    pm10_values = [data.pm10 for data in all_time_data]
    mean_pm25 = mean(pm25_values)
    mean_pm10 = mean(pm10_values)
    
    anomalies = []
    for data in all_time_data:
        if data.pm25 - mean_pm25 > 3 * stdev(pm25_values) or data.pm10 - mean_pm10 > 3 * stdev(pm10_values):
            anomalies.append(data)
    anomalies = anomalies[-5:]
    
    time_intervals = {
        "All Time": (datetime.now() - timedelta(days=365*10), datetime.now()),
        "Last Year": (datetime.now() - timedelta(days=365), datetime.now()),
        "Last Month": (datetime.now() - timedelta(days=30), datetime.now())
    }
    
    start_date, end_date = time_intervals["All Time"]
    
    interval_data = crud.get_data_for_period(db, esp_name, start_date, end_date)
    interval_dates = [data.timestamp for data in interval_data]
    interval_pm25 = [data.pm25 for data in interval_data]
    interval_pm10 = [data.pm10 for data in interval_data]
    
    last_5_data = crud.get_last_n_data(db, esp_name, n=5)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=interval_dates, y=interval_pm25, mode='lines', name='PM2.5', line=dict(color="black")))
    fig.add_trace(go.Scatter(x=interval_dates, y=interval_pm10, mode='lines', name='PM10', line=dict(color="gray")))
    
    fig.add_shape(
        dict(type="line", x0=min(interval_dates), y0=25, x1=max(interval_dates), y1=25, line=dict(color="yellow", width=5))
    )
    fig.add_shape(
        dict(type="line", x0=min(interval_dates), y0=50, x1=max(interval_dates), y1=50, line=dict(color="red", width=5))
    )
    
    fig.update_layout(title='Sensor Data', xaxis_title='Date', yaxis_title='Value')
    graph_html = fig.to_html(full_html=False, default_height=500, default_width=700)
    
    return templates.TemplateResponse("sensor.html", {"request": request, "graph": graph_html, "last_5_data": last_5_data, "mean_pm25": mean_pm25, "mean_pm10": mean_pm10, "anomalies": anomalies})


@app.post("/clients/")
def create_client(request: Request, db: Session = Depends(get_db)):
    new_client = models.Clients(esp_name=models.client.esp_name, password=models.client.password)
    db.add(new_client)
    db.commit()
    db.refresh(new_client)
    
    return new_client

@app.delete("/data/")
def delete_data(request: Request, db: Session = Depends(get_db)):
    data_to_delete = db.query(models.Data).filter(
        and_(
            models.Data.esp_name == request.esp_name,
            models.Data.timestamp >= request.start_date,
            models.Data.timestamp <= request.end_date
        )
    ).all()

    if not data_to_delete:
        raise HTTPException(status_code=404, detail="No data found for the given criteria")

    # Delete the data
    db.query(models.Data).filter(
        and_(
            models.Data.esp_name == request.esp_name,
            models.Data.timestamp >= request.start_date,
            models.Data.timestamp <= request.end_date
        )
    ).delete(synchronize_session=False)

    db.commit()

    return {"message": "Data deleted successfully"}