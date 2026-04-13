import uuid
from typing import Dict, List

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from pydantic import BaseModel

router = APIRouter()

class EvaluationResult(BaseModel):
    score: float
    verdict: str
    missing_requirements: List[str]
    justification: str

# Placeholder in-memory store; an async processing worker should populate this in production.
evaluation_results: Dict[str, EvaluationResult] = {}

@router.post("/upload", status_code=status.HTTP_202_ACCEPTED)
async def upload_file(file: UploadFile = File(...)):
    evaluation_id = str(uuid.uuid4())

    # The file is accepted for asynchronous processing elsewhere.
    return {"evaluation_id": evaluation_id}

@router.get("/result/{evaluation_id}", response_model=EvaluationResult)
async def get_evaluation_result(evaluation_id: str):
    result = evaluation_results.get(evaluation_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evaluation result not found",
        )
    return result
