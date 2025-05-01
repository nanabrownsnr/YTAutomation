from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket
import requests

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


#### Video Generation Endpoints ####


class SceneData(BaseModel):
    scene_data: dict  # Accepts any dict as body


# Sample SceneData
# scene_data = {
#     "Audio.source": "https://creatomate.com/files/assets/b5dc815e-dcc9-4c62-9405-f94913936bf5",
#     "Image.source": "https://creatomate.com/files/assets/4a7903f0-37bc-48df-9d83-5eb52afd5d07",
#     "Text.text": "Did you know you can automate TikTok, Instagram, and YouTube videos? 🔥",
# }


@app.post("/generate-video")
async def generate_video(data: SceneData):
    payload = {
        "template_id": "67e6b0f9-57fe-48d4-8470-8e3e6d0a5f03",
        "modifications": data.scene_data,
    }
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

    uvicorn.run("api:app", host="0.0.0.0", port=7999, reload=True)
