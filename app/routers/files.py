from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
import shutil
import os
from app.dependencies import get_current_user
from app.config import UPLOADS_DIR

router = APIRouter()

@router.post("/upload/receipt")
async def upload_receipt(file: UploadFile = File(...), current_user = Depends(get_current_user)):
    if file.content_type not in ["image/jpeg", "image/png", "application/pdf"]:
        raise HTTPException(status_code=400, detail="Invalid file type")
    
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    file_path = os.path.join(UPLOADS_DIR, f"{file.filename}")
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {"filename": file.filename, "path": file_path}
