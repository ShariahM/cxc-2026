from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import analysis, upload

app = FastAPI(
    title="NFL Footage Analysis API",
    description="API for analyzing NFL video footage",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(upload.router, prefix="/api/upload", tags=["upload"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])

@app.get("/")
async def root():
    return {
        "message": "NFL Footage Analysis API",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
