from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
import requests
from bson import ObjectId
from pydub import AudioSegment
from tempfile import NamedTemporaryFile
import base64
import mimetypes
import os

load_dotenv()

# Environment variables
MONGO_URI = os.getenv("MONGO_URI")
try:
    client = AsyncIOMotorClient(MONGO_URI)
    db = client["YT-files"]  # This is a Motor database
    fs = AsyncIOMotorGridFSBucket(db)
    print("MongoDB connection established and file storage set.")
except Exception as e:
    print(f"MongoDB connection error: {str(e)}")
CREATOMATE_API_KEY = os.getenv("CREATOMATE_API_KEY")

app = FastAPI()

#### File Storage Endpoints ####


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    upload_stream = fs.open_upload_stream(file.filename)
    await upload_stream.write(contents)
    await upload_stream.close()
    return {"file_id": f"{upload_stream._id}"}


@app.get("/file/{file_id}")
async def get_file(file_id: str):
    from bson import ObjectId

    download_stream = await fs.open_download_stream(ObjectId(file_id))
    return StreamingResponse(download_stream, media_type="application/octet-stream")


class FileUpload(BaseModel):
    filename: str
    file_data: str  # Base64 string


@app.post("/upload-base64")
async def upload_base64(payload: FileUpload):
    try:
        binary_data = base64.b64decode(payload.file_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid base64 data")

    # Upload to GridFS
    file_id = await fs.upload_from_stream(payload.filename, binary_data)
    file_id = str(file_id)

    return {"file_id": file_id}



if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="0.0.0.0", port=7999)
