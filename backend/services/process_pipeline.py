from pathlib import Path
from services.frame_extract import extract_frames
from services.detection import run_yolo

def process_pipeline(video_id: str):
    print(video_id)
    video_path = Path("uploads") / video_id
    frames_dir = Path("frames") / video_id
    detections_path = Path("detections") / f"{video_id}.json"

    extract_frames(video_path, frames_dir, fps=7)
    run_yolo(frames_dir, detections_path)

