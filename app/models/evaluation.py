from sqlalchemy import Column, String, Integer, Text
from sqlalchemy.orm import Session

from app.core.database import Base

class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(String, primary_key=True)
    status = Column(String, default="pending")
    score = Column(Integer, nullable=True)
    verdict = Column(String, nullable=True)
    missing_requirements = Column(Text, nullable=True)
    justification = Column(Text, nullable=True)
