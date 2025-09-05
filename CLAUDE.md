# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TagFace is an AI-powered face detection and video segmentation tool that automatically downloads videos from YouTube playlists, performs face detection and tracking, and intelligently segments video clips containing specific faces.

**Key Technologies:**
- Face detection: InsightFace, face_alignment, face_recognition
- Video processing: MoviePy, FFmpeg
- Data processing: NumPy, Pandas
- YouTube downloads: yt-dlp
- GPU acceleration: PyTorch, CUDA support

## Architecture

### Core Processing Pipeline
The project follows a three-stage pipeline:
1. **Download Stage**: YouTube playlist extraction and video downloading
2. **Fragment Stage**: Basic face detection and rough video segmentation  
3. **Capture Stage**: Advanced face tracking and precise segment extraction

### Core Modules (`core/`)
- `_site_.py` - Site class: YouTube playlist management and video downloading
- `__init__.py` - Module exports (currently only imports Site class)

### Foundation Modules (`foundation/`)
- `_getPath_.py` - Path utility function with automatic directory creation
- `_operation_.py` - Operation class: Multi-processing pipeline for parallel video processing
- `__init__.py` - Foundation module exports

### Main Processing Scripts
- `script-download-video.py` - Downloads videos from YouTube playlists using Site class
- `script-capture-face.py` - Face detection with tracking using face_alignment and face_recognition (Knife class)
- `script-cut-fragment.py` - Video segmentation using InsightFace for detection (Hatchet class)

### Key Classes and Their Responsibilities
- **Site** (`core/_site_.py`): YouTube playlist extraction and video downloading with yt-dlp
- **Operation** (`foundation/_operation_.py`): Multi-processing executor with concurrent.futures
- **Knife** (`script-capture-face.py`): Advanced face detection using face_alignment + face_recognition
- **Hatchet** (referenced in `script-cut-fragment.py`): Basic face detection using InsightFace  
- **Element** (`script-cut-fragment.py`): Time interval management for video segments
- **Transition** (`script-capture-face.py`): State management for face tracking continuity

### Data Structure
```
download/[playlist_name]/
  ├── playlist.csv          # Playlist metadata (in video/ subdirectory)
  ├── video/               # Downloaded video files (.mp4, .mkv, .webm)
  ├── #face/               # Face detection CSV files and cropped video segments
  └── #fragment/           # Generated video fragments from basic face detection

version/                   # Version-specific processing results
```

## Development Commands

### Install Dependencies
```bash
# Core dependencies for the current implementation
pip install torch torchvision face_alignment moviepy yt_dlp pandas numpy pillow scikit-image tqdm insightface face_recognition
```

### Install FFmpeg (Required)
- Windows: Download FFmpeg and add to PATH
- macOS: `brew install ffmpeg` 
- Linux: `sudo apt install ffmpeg`

### Download Videos
```bash
# Edit script-download-video.py to set playlist URL and storage path
python script-download-video.py
```

### Process Videos (Face Detection & Segmentation)
```bash
# Two-step processing pipeline:

# Step 1: Basic face detection and segmentation (Hatchet class with InsightFace)
python script-cut-fragment.py     # Creates fragments in #fragment directory

# Step 2: Advanced face detection with tracking (Knife class with face_alignment + face_recognition)
python script-capture-face.py     # Processes fragments, creates tracked segments in #face directory
```

### Processing Pipeline Flow
1. **Download**: `script-download-video.py` downloads YouTube playlist videos to `download/[playlist]/video/`
2. **Fragment**: `script-cut-fragment.py` creates basic video fragments using InsightFace detection, outputs to `#fragment/`
3. **Track**: `script-capture-face.py` performs advanced face tracking on fragments with IoU-based continuity, outputs to `#face/`

### Face Tracking Algorithm Details
The face tracking system uses sophisticated continuity analysis:
- **IoU Tracking**: Uses `torchvision.ops.box_iou()` with 0.6 threshold for bounding box overlap detection
- **Face Recognition**: Uses `face_recognition.face_distance()` with 0.5 threshold for facial feature matching
- **State Management**: Transition class manages face tracking state across video frames
- **Connection Logic**: Implements bipartite matching between detected faces and existing tracks
- **Trajectory Building**: Creates continuous face trajectories with time intervals and bounding box regions

## Code Style Guidelines

This project follows specific Python coding conventions:

### Syntax Style
- Conditional statements: `if(condition==True):`
- Return statements: `return(value)` 
- Use `pass` statements at end of code blocks
- Create logical blocks with `if(True):`

### Function Definitions
```python
def functionName(parameter: type, another: type) -> type:
    # Function implementation
    return(result)
```

### Class Definitions  
```python
class ClassName:
    
    def __init__(self, param: type) -> None:
        self.param = param
        return
    
    pass
```

### Error Handling
```python
try:
    operation()
    pass
except:
    cleanup()
    return(True)
```

### Comments
- Use Traditional Chinese for code comments
- Document function parameters and return values
- Explain complex algorithms and thresholds

### Import Style
```python
# Each import on separate line
import os
import numpy  
import pandas
```

## Working with This Codebase

### Face Detection Pipeline
1. **Video Download**: Use Site class (`core._site_.py`) to download from YouTube playlists
2. **Face Detection**: Use face_alignment and face_recognition libraries for detection
3. **Tracking**: IoU-based bounding box tracking and face_recognition distance-based matching
4. **Segmentation**: Element class manages time intervals and fragment extraction

### Key Parameters
- Face detection interval: Every 25 frames (adjustable)
- IoU threshold: 0.6 for face tracking (`getContinuity` function)
- Face distance threshold: 0.5 for face_recognition matching
- Minimum segment length: 2 seconds
- Multi-processing: Configurable via `Operation` class (number and chunk parameters)

### Hardware Requirements
- **GPU**: NVIDIA with CUDA support recommended (4GB+ VRAM)
- **RAM**: 8GB+ recommended
- **Storage**: Sufficient space for videos and segments

## Important Notes

- Follow existing code style conventions exactly
- Use Traditional Chinese comments for consistency
- Maintain the specific syntax patterns (parentheses around conditions/returns)
- Functions use descriptive English names with type hints
- Classes use single noun names
- Always use `pass` statements and proper indentation
- Handle exceptions with simple try/except blocks returning `True`
- Respect YouTube's terms of service and copyright policies

## Testing & Validation

- No formal test framework - verify functionality manually
- Check GPU memory usage during face detection
- Monitor processing performance and storage usage
- Validate video quality and segment accuracy