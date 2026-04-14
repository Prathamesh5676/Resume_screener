from typing import Optional

from app.workers.celery_app import celery
from app.services.pdf_service import extract_text
from app.services.llm_service import evaluate_resume
from app.models.evaluation import Evaluation
from app.core.database import SessionLocal
import json


@celery.task
def process_resume(evaluation_id: str, file_bytes: bytes, jd_text: Optional[str] = None):
    print("TASK STARTED:", evaluation_id)

    db = SessionLocal()

    try:
        print("Extracting text...")

        resume_text = extract_text(file_bytes)
        print("Extracted length:", len(resume_text))

        # Check if text extraction worked
        if not resume_text or len(resume_text.strip()) < 10:
            print("ERROR: Resume text extraction failed or too short!")
            raise ValueError("Resume text extraction failed")

        # Check for common resume keywords to verify extraction
        resume_keywords = ['experience', 'education', 'skills', 'project', 'work', 'python', 'java', 'javascript']
        _ = [kw for kw in resume_keywords if kw.lower() in resume_text.lower()]

        if not jd_text or not jd_text.strip():
            jd_text = """
            We are hiring a Backend Engineer.

            Mandatory:
            - Strong Python experience (3+ years)
            - FastAPI or Django
            - PostgreSQL
            - Docker (must)
            - AWS (EC2, S3)
            - REST API design

            Preferred:
            - Redis
            - Kubernetes
            - CI/CD

            Reject candidates without backend experience.
            """

        print("Calling LLM with jd_text and resume_text...")
        result = evaluate_resume(jd_text, resume_text)
        print("LLM RESULT:", result)

        evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()

        if evaluation:
            print("Updating DB...")

            evaluation.score = result["score"]
            evaluation.verdict = result["verdict"]
            evaluation.missing_requirements = result["missing_requirements"]
            evaluation.justification = result["justification"]
            evaluation.status = "completed"

            db.commit()

            print("DONE")

    except Exception as e:
        print("WORKER ERROR:", str(e))

        evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()
        if evaluation:
            evaluation.status = "failed"
            evaluation.justification = str(e)
            db.commit()

    finally:
        db.close()