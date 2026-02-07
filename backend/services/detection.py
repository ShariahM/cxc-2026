from ultralytics import YOLO
from pathlib import Path
import json

def run_yolo(frames_dir: Path, output_json: Path):
    model = YOLO("yolos/best.pt")

    results = model.track(
        source=str(frames_dir),
        tracker="yolos/bytetrack.yaml",
        conf=0.3,
        iou=0.5,
        persist=True,
        classes=[0],  # Only detect people
        imgsz=640,
        save=True   
    )

    output = {}

    for r in results:
        frame_name = Path(r.path).name
        output[frame_name] = []

        # Skip frames with no detections
        if r.boxes is None or len(r.boxes) == 0:
            continue

        # Make sure track IDs exist (ByteTrack may assign None)
        if r.boxes.id is None:
            continue

        for box, track_id in zip(r.boxes.xyxy, r.boxes.id):
            output[frame_name].append({
                "track_id": int(track_id),
                "x1": float(box[0]),
                "y1": float(box[1]),
                "x2": float(box[2]),
                "y2": float(box[3]),
            })

    # Save JSON
    with open(output_json, "w") as f:
        json.dump(output, f, indent=2)
