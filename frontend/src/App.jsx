import { useState } from 'react';
import './App.css';

function App() {
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.type.startsWith('video/')) {
      setFile(droppedFile);
    }
  };

  const handleFileInput = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      uploadVideo(selectedFile, 1, )
    }
  };

  async function uploadVideo(file, setVideoId) {

  const formData = new FormData();
  formData.append("file", file);
  let modified_name;
  try {
    const res = await fetch("http://localhost:8000/api/upload/video", {
      method: "POST",
      body: formData
    });

    if (!res.ok) {
      throw new Error("Upload failed");
    }



    const data = await res.json();
    modified_name = data.filename;

  } catch (err) {
    console.error(err);
    alert("Upload failed");
  }
  finally {
    const res2 = await fetch("http://localhost:8000/api/analysis/start", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        filename: modified_name
      })
    });
  }
}


  const handleClear = () => {
    setFile(null);
  };

  return (
    <div className="app">
      <div className="container">
        <h1>NFL Footage Analysis</h1>
        
        <div
          className={`dropbox ${isDragging ? 'dragging' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          {!file ? (
            <div className="dropbox-content">
              <p className="dropbox-text">Drag & drop video file here</p>
              <p className="dropbox-or">or</p>
              <label htmlFor="file-input" className="file-label">
                Browse Files
              </label>
              <input
                id="file-input"
                type="file"
                accept="video/*"
                onChange={handleFileInput}
                className="file-input"
              />
            </div>
          ) : (
            <div className="file-info">
              <p className="file-name">{file.name}</p>
              <p className="file-size">{(file.size / (1024 * 1024)).toFixed(2)} MB</p>
              <button onClick={handleClear} className="clear-button">
                Clear
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
