from sqlalchemy import Column, Integer, String, DATETIME
from database import Base

class Data(Base):
    __tablename__ = "data"

    id = Column(Integer, primary_key=True)
    pm25 = Column(Integer)
    pm10 = Column(Integer)
    esp_name = Column(String)
    timestamp = Column(DATETIME)