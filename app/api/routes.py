import uuid

from fastapi import APIRouter, File, UploadFile, status

router = APIRouter()

@router.post("/upload", status_code=status.HTTP_202_ACCEPTED)
async def upload_file(file: UploadFile = File(...)):
    evaluation_id = str(uuid.uuid4())

    # The file is accepted for asynchronous processing elsewhere.
    return {"evaluation_id": evaluation_id}
