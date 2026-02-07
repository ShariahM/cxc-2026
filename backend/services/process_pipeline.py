from fastapi import Path
from services.frame_extract import extract_frames
from services.detection import run_yolo
import cv2

def process_pipeline(video_id: str):
    video_path = Path("uploads") / video_id
    frames_dir = Path("data/frames") / video_id
    detections_path = Path("data/detections") / f"{video_id}.json"

    extract_frames(video_path, frames_dir, fps=5)
    run_yolo(frames_dir, detections_path)
    
