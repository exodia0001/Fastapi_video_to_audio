from fastapi import FastAPI, File, UploadFile, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil
from moviepy.editor import VideoFileClip
from pathlib import Path

def video_to_audio(filename: str) -> str:
    video = VideoFileClip(filename)
    new_filename = filename.rsplit(".", 1)[0] + ".mp3"  # Include the .mp3 extension
    video.audio.write_audiofile(new_filename)
    video.close()
    return new_filename

def delete_file(path: str):
    os.remove(path)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def hello():
    return {"greeting": "hello"}

@app.post("/convert-file")
async def convert(fileb: UploadFile = File(), background_tasks: BackgroundTasks = None):
    temp_file_path = fileb.filename  # Create the temp file in the current directory
    with open(temp_file_path, "wb") as temp_file:
        shutil.copyfileobj(fileb.file, temp_file)
        fileb.file.close()
    
    new_file_path = video_to_audio(temp_file_path)
    audio_path = Path(new_file_path)

    os.remove(temp_file_path)

    background_tasks.add_task(delete_file, new_file_path)
    return FileResponse(audio_path, media_type='audio/mpeg')
