import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def test_full_pipeline():
    # Note: You'll need a sample_resume.pdf file in the tests directory
    files = {"file": open("tests/sample_resume.pdf", "rb")}

    # Step 1: Upload
    response = requests.post(f"{BASE_URL}/add_data", files=files)
    assert response.status_code == 202

    evaluation_id = response.json()["evaluation_id"]
    print(f"Upload successful. Evaluation ID: {evaluation_id}")

    # Step 2: Poll result
    for attempt in range(30):  # Increased timeout for LLM processing
        result = requests.get(f"{BASE_URL}/result/{evaluation_id}")
        assert result.status_code == 200

        data = result.json()
        print(f"Attempt {attempt + 1}: Status = {data['status']}")

        if data["status"] == "completed":
            # Verify all required fields are present
            assert "score" in data
            assert "verdict" in data
            assert "missing_requirements" in data
            assert "justification" in data

            # Verify data types
            assert isinstance(data["score"], int) or data["score"] is None
            assert isinstance(data["verdict"], str) or data["verdict"] is None
            assert isinstance(data["missing_requirements"], str) or data["missing_requirements"] is None
            assert isinstance(data["justification"], str) or data["justification"] is None

            print("Pipeline test passed!")
            print(f"Score: {data['score']}")
            print(f"Verdict: {data['verdict']}")
            return

        elif data["status"] == "failed":
            assert False, f"Processing failed: {data.get('justification', 'Unknown error')}"

        time.sleep(3)  # Wait 3 seconds between polls

    assert False, "Processing timeout - took longer than 90 seconds"

if __name__ == "__main__":
    test_full_pipeline()