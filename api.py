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


#### Video Generation Endpoints ####


class SceneData(BaseModel):
    scene_data: dict  # Accepts any dict as body


# Sample SceneData
# scene_data =

# scene_data = {
#     "template_id": "50c3028d-2255-4c7d-b284-aa117fe28672",
#     "modifications": {
#         "Audio-1.source": "https://creatomate.com/files/assets/b5dc815e-dcc9-4c62-9405-f94913936bf5",
#         "Image-1.source": "https://creatomate.com/files/assets/4a7903f0-37bc-48df-9d83-5eb52afd5d07",
#         "Text-1.text": "Did you know you can automate TikTok, Instagram, and YouTube videos? 🔥",
#         "Audio-2.source": "https://creatomate.com/files/assets/b5dc815e-dcc9-4c62-9405-f94913936bf5",
#         "Image-2.source": "https://creatomate.com/files/assets/4a7903f0-37bc-48df-9d83-5eb52afd5d07",
#         "Text-2.text": "Did you know you can automate TikTok, Instagram, and YouTube videos? 🔥",
#         "Audio-3.source": "https://creatomate.com/files/assets/b5dc815e-dcc9-4c62-9405-f94913936bf5",
#         "Image-3.source": "https://creatomate.com/files/assets/4a7903f0-37bc-48df-9d83-5eb52afd5d07",
#         "Text-3.text": "Did you know you can automate TikTok, Instagram, and YouTube videos? 🔥",
#         "Audio-4.source": "https://creatomate.com/files/assets/b5dc815e-dcc9-4c62-9405-f94913936bf5",
#         "Image-4.source": "https://creatomate.com/files/assets/4a7903f0-37bc-48df-9d83-5eb52afd5d07",
#         "Text-4.text": "Did you know you can automate TikTok, Instagram, and YouTube videos? 🔥",
#         "Audio-5.source": "https://creatomate.com/files/assets/b5dc815e-dcc9-4c62-9405-f94913936bf5",
#         "Image-5.source": "https://creatomate.com/files/assets/4a7903f0-37bc-48df-9d83-5eb52afd5d07",
#         "Text-5.text": "Did you know you can automate TikTok, Instagram, and YouTube videos? 🔥",
#     },
#     "webhook_url": "",
# }


@app.post("/generate-video")
async def generate_video(data: SceneData):
    payload = data.scene_data
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CREATOMATE_API_KEY}",
    }

    response = requests.post(
        "https://api.creatomate.com/v1/renders", json=payload, headers=headers
    )
    return response.json()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="0.0.0.0", port=7999)
