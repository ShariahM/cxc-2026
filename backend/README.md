# NFL Footage Analysis Backend

A barebones FastAPI backend for analyzing NFL video footage.

## Project Structure

```
backend/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── api/                    # API route handlers
│   ├── __init__.py
│   ├── upload.py          # Video upload endpoints
│   └── analysis.py        # Video analysis endpoints
├── models/                 # Data models
│   ├── __init__.py
│   └── video.py           # Video-related Pydantic models
├── services/               # Business logic layer
│   ├── __init__.py
│   └── video_analysis.py  # Video analysis service
├── utils/                  # Utility functions
│   ├── __init__.py
│   └── helpers.py         # Helper functions
└── uploads/                # Video file storage (created at runtime)
```

## Folder Explanations

### `api/`
**Purpose**: Contains all API route handlers (endpoints)

**How to use**:
- Each file represents a group of related endpoints
- `upload.py`: Handles video file uploads, listing, and deletion
- `analysis.py`: Handles video analysis requests and results
- Add new router files here for additional API features
- Import and register new routers in `main.py`

**Example**: Adding a new router
```python
# api/players.py
from fastapi import APIRouter
router = APIRouter()

@router.get("/list")
async def list_players():
    return {"players": []}

# Then in main.py:
from api import players
app.include_router(players.router, prefix="/api/players", tags=["players"])
```

### `models/`
**Purpose**: Defines data structures using Pydantic models

**How to use**:
- Create models for request/response validation
- Define database schemas (if using a database)
- `video.py`: Contains video metadata and analysis result models
- Add new model files for different data entities

**Example**: Adding a new model
```python
# models/player.py
from pydantic import BaseModel

class Player(BaseModel):
    id: int
    name: str
    position: str
    team: str
```

### `services/`
**Purpose**: Contains business logic and core functionality

**How to use**:
- Implement your video analysis algorithms here
- Keep API routes clean by moving logic to services
- `video_analysis.py`: Service for processing and analyzing videos
- Add ML model loading, video processing, data extraction here

**Example**: Implementing analysis logic
```python
# services/video_analysis.py
import cv2

class VideoAnalysisService:
    async def analyze_video(self, filename: str):
        # Load video with OpenCV
        cap = cv2.VideoCapture(f"uploads/{filename}")
        
        # Process frames
        # Run ML models
        # Extract data
        
        return results
```

### `utils/`
**Purpose**: Reusable utility functions and helpers

**How to use**:
- Add common helper functions here
- File operations, validation, formatting
- `helpers.py`: Contains file utilities and validators
- Keep functions generic and reusable

**Example**: Using utilities
```python
from utils.helpers import format_file_size, validate_video_format

size_str = format_file_size(1024000)  # "1.00 MB"
is_valid = validate_video_format("video.mp4")  # True
```

### `uploads/`
**Purpose**: Stores uploaded video files

**How to use**:
- Created automatically when first video is uploaded
- Files are saved with timestamps to avoid collisions
- Configure in `api/upload.py` - UPLOAD_DIR variable
- Consider moving to cloud storage (S3, Azure Blob) for production

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
```

2. Activate the virtual environment:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

Development server:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs (Swagger): http://localhost:8000/docs
- Alternative docs (ReDoc): http://localhost:8000/redoc

## API Endpoints

### Upload Routes (`/api/upload`)
- `POST /api/upload/video` - Upload a video file
- `GET /api/upload/list` - List all uploaded videos
- `DELETE /api/upload/{filename}` - Delete an uploaded video

### Analysis Routes (`/api/analysis`)
- `POST /api/analysis/start` - Start video analysis
- `GET /api/analysis/status/{filename}` - Get analysis status
- `GET /api/analysis/results/{filename}` - Get analysis results

## Adding Your Analysis Logic

1. **Install additional packages** (if needed):
```bash
pip install opencv-python numpy tensorflow pytorch
# Update requirements.txt
pip freeze > requirements.txt
```

2. **Implement analysis in `services/video_analysis.py`**:
- Load your ML models
- Process video frames
- Extract relevant data
- Return structured results

3. **Update `api/analysis.py`**:
- Import your service
- Call service methods from endpoints
- Handle errors appropriately

4. **Add models in `models/`**:
- Define response structures
- Validate input data

## Best Practices

- Keep routes thin, move logic to services
- Use Pydantic models for validation
- Handle exceptions properly
- Add logging for debugging
- Use async/await for I/O operations
- Document your code with docstrings
- Write tests for critical functionality

## Next Steps

- [ ] Implement actual video analysis logic in `services/video_analysis.py`
- [ ] Add database integration (SQLAlchemy, MongoDB, etc.)
- [ ] Implement authentication and authorization
- [ ] Add logging and monitoring
- [ ] Write unit tests
- [ ] Set up CI/CD pipeline
- [ ] Configure production settings
- [ ] Add rate limiting and security measures
