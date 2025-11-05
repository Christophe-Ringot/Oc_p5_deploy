from sqlalchemy import Column, Integer, Float, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)

    employee_id = Column(Integer)
    prediction = Column(Integer)
    probability = Column(Float)
    probabilities = Column(JSON)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Prediction(id={self.id}, employee_id={self.employee_id}, prediction={self.prediction}, probability={self.probability})>"
