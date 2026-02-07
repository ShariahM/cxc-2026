from ultralytics import YOLO
from pathlib import Path
from services.player_classification import get_player_color, cluster_players
import cv2
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
        frame_path = frames_dir / frame_name

        frame = cv2.imread(str(frame_path))  # 👈 load image

        output[frame_name] = []

        if r.boxes is None or len(r.boxes) == 0 or r.boxes.id is None:
            continue

        colors = []
        valid = []

        # PASS 1 — gather colors
        for box, track_id in zip(r.boxes.xyxy, r.boxes.id):
            color = get_player_color(frame, box)

            if color is not None:
                colors.append(color)
                valid.append((box, track_id))

        # PASS 2 — cluster
        teams = cluster_players(colors)

        # PASS 3 — write JSON
        for (box, track_id), team in zip(valid, teams):
            output[frame_name].append({
                "track_id": int(track_id),
                "x1": float(box[0]),
                "y1": float(box[1]),
                "x2": float(box[2]),
                "y2": float(box[3]),
                "team": int(team)
            })

    # Save JSON
    with open(output_json, "w") as f:
        json.dump(output, f, indent=2)
