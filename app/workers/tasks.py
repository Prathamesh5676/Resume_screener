from app.workers.celery_app import celery
from app.services.pdf_service import extract_text
from app.services.llm_service import evaluate_resume
from app.models.evaluation import Evaluation
from app.core.database import SessionLocal
import json


@celery.task
def process_resume(evaluation_id: str, file_bytes: bytes):
    print("🔥 TASK STARTED:", evaluation_id)

    db = SessionLocal()

    try:
        print("📄 Extracting text...")
        resume_text = extract_text(file_bytes)
        print("📄 Extracted length:", len(resume_text))
        print("📄 FIRST 200 CHARS:", resume_text[:200]) 

        jd_text = jd_text = """
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

        print("🤖 Calling LLM...")
        result = evaluate_resume(jd_text, resume_text)
        print("✅ LLM RESULT:", result)

        evaluation = db.query(Evaluation).filter(Evaluation.id == evaluation_id).first()

        if evaluation:
            print("💾 Updating DB...")

            evaluation.score = result["score"]
            evaluation.verdict = result["verdict"]
            evaluation.missing_requirements = result["missing_requirements"]
            evaluation.justification = result["justification"]
            evaluation.status = "completed"

            db.commit()

            print("🎉 DONE")

    except Exception as e:
        print("❌ WORKER ERROR:", e)

    finally:
        db.close()