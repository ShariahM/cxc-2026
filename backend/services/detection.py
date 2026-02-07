from ultralytics import YOLO
from pathlib import Path
import json

model = YOLO("yolov8x.pt")

def run_yolo(frames_dir: Path, output_json: Path):
    results = {}

    for frame_path in sorted(frames_dir.glob("*.jpg")):
        yolo_results = model.track(
        source=str(frames_dir),
        tracker="bytetrack.yaml",
        conf=0.4,
        iou=0.5,
        persist=True,
        stream=True  # important!
    )

        detections = []
        for box in yolo_results[0].boxes:
            cls_id = int(box.cls[0])
            # COCO class 0 = person
            if cls_id != 0:
                continue

            x1, y1, x2, y2 = box.xyxy[0].tolist()

            detections.append({
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
                "confidence": float(box.conf[0])
            })

        
        results[frame_path.name] = detections

    with open(output_json, "w") as f:
        json.dump(results, f, indent=2)
