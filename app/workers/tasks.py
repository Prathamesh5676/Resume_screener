from app.workers.celery_app import celery
from app.services.pdf_service import extract_text
from app.services.llm_service import evaluate_resume
from app.models.evaluation import Evaluation
from app.core.database import SessionLocal


@celery.task
def process_resume(evaluation_id: str, file_bytes: bytes):
    db = SessionLocal()

    try:
        # 1. Extract text from PDF
        resume_text = extract_text(file_bytes)

        # 2. Dummy JD (replace later with real input)
        jd_text = "Looking for Python developer with FastAPI experience"

        # 3. Call LLM
        result = evaluate_resume(jd_text, resume_text)

        # 4. Update DB
        evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()

        if evaluation:
            evaluation.score = result["score"]
            evaluation.verdict = result["verdict"]
            evaluation.missing_requirements = str(result["missing_requirements"])
            evaluation.justification = result["justification"]
            evaluation.status = "completed"

            db.commit()

    except Exception as e:
        print("Worker Error:", e)

    finally:
        db.close()