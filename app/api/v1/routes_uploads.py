# app/api/v1/routes_uploads.py
from fastapi import APIRouter, UploadFile, File, HTTPException
import httpx
import requests
# import base64
import os
from dotenv import load_dotenv

load_dotenv()
router = APIRouter(tags=["uploads"])

IMAGEKIT_UPLOAD_URL = "https://upload.imagekit.io/api/v1/files/upload"
IMAGEKIT_PRIVATE_KEY = os.getenv("IMAGEKIT_PRIVATE_KEY")

@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    try:
        file_bytes = await file.read()

        files_payload = {
            "file": (file.filename, file_bytes, file.content_type)
        }

        data_payload = {
            "fileName": file.filename,
            "folder": "/events"
        }
        async with httpx.AsyncClient() as client:
            res = await client.post(
                IMAGEKIT_UPLOAD_URL,
                auth=(IMAGEKIT_PRIVATE_KEY, ""),  # basic auth
                files=files_payload,
                data=data_payload
            )

        if res.status_code != 200:
            print(f"ImageKit Error: {res.status_code}", res.text)
            raise HTTPException(status_code=400, detail=f"ImageKit Upload Failed: {res.text}")

        data = res.json()
        return {
            "url": data["url"],
            "thumbnail": data.get("thumbnailUrl"),
            "name": data["name"],
        }
    except Exception as e:
        print(f"Upload Exception: {e}")
        raise HTTPException(status_code=500, detail=str(e))
