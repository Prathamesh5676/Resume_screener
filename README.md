# 📄 Resume Screening System

## 🚀 Architecture Overview

This system is designed as an **asynchronous resume evaluation pipeline** using modern backend and AI tools.

### 🔧 Tech Stack

* **FastAPI** → API layer for handling requests
* **Celery** → Background worker for async processing
* **Redis** → Message broker between API and worker
* **Groq LLM API** → Resume evaluation engine
* **SQLite** → Persistent storage for results
* **Docker** → Containerized deployment

---

### 🔄 System Flow

1. Client uploads resume via `/upload`
2. FastAPI:
   * Stores evaluation record (status = pending)
   * Sends task to Celery
   * Returns `evaluation_id` immediately
3. Celery Worker:
   * Extracts resume text
   * Calls LLM for evaluation
   * Saves structured result to DB
4. Client polls `/result/{evaluation_id}`

---

### 📊 Architecture Diagram (Logical)

Client → FastAPI → Redis Queue → Celery Worker → LLM → Database → Client

---

## ⚙️ Setup Instructions (Dockerized)

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd resume_screener
```

---

### 2. Create `.env` file

```env
GROQ_API_KEY=your_api_key_here
```

---

### 3. Build and Run Containers

```bash
docker-compose up --build
```

---

### 4. Verify Services

* FastAPI → http://localhost:8000/docs
* Redis → running on port 6379
* Celery → running in background

---

## 🔌 API Usage

---

### POST `/upload`

Upload resume PDF file and provide the job description as plain text:

```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@resume.pdf" \
  -F "job_description=We are hiring a Backend Engineer.\n\nMandatory:\n- Strong Python experience (3+ years)\n- FastAPI or Django\n- PostgreSQL\n- Docker (must)\n- AWS (EC2, S3)\n- REST API design\n\nPreferred:\n- Redis\n- Kubernetes\n- CI/CD"
```

Response:

```json
{
  "evaluation_id": "uuid"
}
```

---

### GET `/result/{evaluation_id}`

Get evaluation result:

```bash
curl http://localhost:8000/result/{evaluation_id}
```

Response:

```json
{
  "status": "completed",
  "score": 85,
  "verdict": "GOOD_MATCH",
  "missing_requirements": ["Docker"],
  "justification": "..."
}
```

---

## 🧪 Testing Instructions

### 🔹 Run Integration Test

```bash
python tests/test_pipeline.py
```

---

### 🔹 What the Test Covers

* Upload endpoint works
* Celery worker processes task
* Redis queue communication
* LLM evaluation completes
* Database updated correctly

---

### 🔹 Expected Flow

```text
Upload → Pending → Processing → Completed
```

---

### 🔹 Manual Testing (Optional)

1. Open Swagger UI:
```
http://localhost:8000/docs
```

2. Upload a resume
3. Copy `evaluation_id`
4. Fetch result

---

## 💼 Sample Job Descriptions

Use any of the following as the `job_description` field when uploading a resume:

---

### 🔹 Backend Developer

We are hiring a backend developer. Candidates must have strong experience in Python, hands-on knowledge of FastAPI or Django, and at least 3 years of backend development experience. Familiarity with PostgreSQL, Docker, AWS services like EC2 and S3, and REST API design is required. Experience with Redis, Kubernetes, and CI/CD pipelines is preferred.

---

### 🔹 Frontend Developer

We are looking for a frontend developer. Applicants should have solid experience with HTML, CSS, and JavaScript, along with at least 2 years of experience using React. Understanding of responsive design and API integration is required. Experience with TypeScript, Next.js, and modern UI frameworks is a plus.

---

### 🔹 Data Analyst

We are hiring a data analyst. Candidates must have strong skills in SQL, data visualization tools like Power BI or Tableau, and experience working with large datasets. Knowledge of Python libraries such as Pandas and NumPy is required. Experience with machine learning and statistical modeling is preferred.

---

## 🛡 Resilience & Reliability

* Retry logic for LLM failures (rate limits, network issues)
* JSON validation for structured output
* Failed tasks marked in database
* Logging for debugging and monitoring

---

## 📌 Notes

* Ensure Docker Desktop is running before starting
* `.env` file must contain valid API key
* Celery worker must be running for processing

---

## ✅ Conclusion

This project demonstrates:

* Asynchronous system design
* Worker queue architecture
* LLM integration with structured output
* End-to-end tested pipeline