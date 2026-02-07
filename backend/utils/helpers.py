from pathlib import Path
from typing import List
import hashlib

def generate_file_hash(file_path: Path) -> str:
    """
    Generate SHA256 hash for a file.
    
    Args:
        file_path: Path to the file
    
    Returns:
        Hexadecimal hash string
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def get_file_extension(filename: str) -> str:
    """
    Extract file extension from filename.
    
    Args:
        filename: Name of the file
    
    Returns:
        File extension (e.g., '.mp4')
    """
    return Path(filename).suffix

def validate_video_format(filename: str, allowed_formats: List[str] = None) -> bool:
    """
    Validate if file has an allowed video format.
    
    Args:
        filename: Name of the file
        allowed_formats: List of allowed extensions (default: common video formats)
    
    Returns:
        True if format is valid, False otherwise
    """
    if allowed_formats is None:
        allowed_formats = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv']
    
    extension = get_file_extension(filename).lower()
    return extension in allowed_formats

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
    
    Returns:
        Formatted size string (e.g., '10.5 MB')
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"
