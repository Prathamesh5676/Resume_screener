import uuid
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.evaluation import Evaluation

router = APIRouter()

class EvaluationResult(BaseModel):
    status: str
    score: Optional[int] = None
    verdict: Optional[str] = None
    missing_requirements: Optional[str] = None
    justification: Optional[str] = None

@router.post("/upload", status_code=status.HTTP_202_ACCEPTED)
async def upload_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    evaluation_id = str(uuid.uuid4())
    
    # Create and save new evaluation record with pending status
    evaluation = Evaluation(
        id=evaluation_id,
        status="pending",
        score=None,
        verdict=None,
        missing_requirements=None,
        justification=None,
    )
    db.add(evaluation)
    db.commit()
    db.refresh(evaluation)

    # The file is accepted for asynchronous processing elsewhere.
    return {"evaluation_id": evaluation_id}

@router.get("/result/{evaluation_id}", response_model=EvaluationResult)
async def get_evaluation_result(evaluation_id: str, db: Session = Depends(get_db)):
    evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
    if evaluation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation result not found",
        )
    return EvaluationResult(
        status=evaluation.status,
        score=evaluation.score,
        verdict=evaluation.verdict,
        missing_requirements=evaluation.missing_requirements,
        justification=evaluation.justification,
    )

# Add dependency to get DB session using FastAPI Depends
# Create get_db() function if not exists