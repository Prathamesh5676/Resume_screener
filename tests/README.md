# Integration Tests

This directory contains integration tests for the Resume Screener application.

## Prerequisites

1. Make sure the application is running:
   ```bash
   # Terminal 1: Start FastAPI server
   uvicorn app.main:app --reload

   # Terminal 2: Start Celery worker
   celery -A app.workers.celery_app worker --loglevel=info --pool=solo

   # Terminal 3: Start Redis (if not already running)
   redis-server
   ```

2. Place a sample PDF resume file named `sample_resume.pdf` in the `tests/` directory

## Running the Integration Test

```bash
cd tests
python test_pipeline.py
```

## What the Test Does

The integration test (`test_pipeline.py`) verifies the complete end-to-end workflow:

1. **Upload**: Sends a resume PDF to `/upload` endpoint
2. **Processing**: Waits for Celery to process the resume via LLM
3. **Result**: Polls `/result/{evaluation_id}` until completion
4. **Validation**: Verifies the response contains all required fields

## Expected Output

```
Upload successful. Evaluation ID: abc-123-def-456
Attempt 1: Status = pending
Attempt 2: Status = pending
...
Attempt 5: Status = completed
Pipeline test passed!
Score: 85
Verdict: GOOD_MATCH
```

## Test Coverage

This test proves that:
- FastAPI endpoints work correctly
- File upload handling works
- Database operations work
- Celery task queuing works
- Redis message broker works
- LLM evaluation works
- Result retrieval works