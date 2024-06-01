from sqlalchemy import Column, Integer, String, DateTime
from database import Base

class Data(Base):
    __tablename__ = "data"

    id = Column(Integer, primary_key=True, index=True)
    pm25 = Column(Integer, nullable=False)
    pm10 = Column(Integer, nullable=False)
    esp_name = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)

class Clients(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    esp_name = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)