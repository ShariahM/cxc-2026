import subprocess
from pathlib import Path

def extract_frames(video_path: Path, output_dir: Path, fps: int = 5):
    """
    Extract frames from video at `fps` frames per second.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    # %04d ensures zero-padded frame numbers
    cmd = [
        "ffmpeg",
        "-i", str(video_path),
        "-vf", f"fps={fps}",
        str(output_dir / "frame_%04d.jpg")
    ]
    subprocess.run(cmd, check=True)
