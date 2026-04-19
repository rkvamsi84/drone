from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse, HTMLResponse
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, auth
import io
import random

router = APIRouter(prefix="/api/video", tags=["video"])

@router.get("/stream/{drone_id}")
async def get_video_stream(
    drone_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """
    WebRTC video streaming endpoint
    Currently returns mock video feed for demo purposes
    """
    # Verify drone exists
    drone = db.query(models.Drone).filter(models.Drone.id == drone_id).first()
    if not drone:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Drone not found")
    
    # Return mock WebRTC connection info
    # In production, this would establish actual WebRTC connection
    return {
        "drone_id": drone_id,
        "drone_name": drone.name,
        "status": "streaming",
        "stream_url": f"/api/video/mock-stream/{drone_id}",
        "webrtc_config": {
            "ice_servers": [
                {"urls": "stun:stun.l.google.com:19302"}
            ]
        },
        "note": "Demo mode - showing mock video feed"
    }

@router.get("/mock-stream/{drone_id}")
async def get_mock_video_stream(drone_id: int):
    """
    Mock video stream - returns demo video for testing
    """
    # Generate a simple mock video feed
    # In production, this would be actual video stream from drone
    return {
        "stream_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
        "type": "demo",
        "drone_id": drone_id,
        "message": "Demo video feed - production would show live drone camera"
    }

@router.get("/player/{drone_id}")
async def get_video_player(drone_id: int):
    """
    HTML video player for live stream
    """
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Live Video Feed - Drone {drone_id}</title>
        <style>
            body {{
                margin: 0;
                padding: 20px;
                background: #1a1a1a;
                color: #fff;
                font-family: Arial, sans-serif;
            }}
            .video-container {{
                max-width: 1280px;
                margin: 0 auto;
                background: #000;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 4px 20px rgba(0,0,0,0.5);
            }}
            video {{
                width: 100%;
                height: auto;
                display: block;
            }}
            .overlay {{
                position: absolute;
                top: 10px;
                left: 10px;
                background: rgba(0,0,0,0.7);
                padding: 10px 15px;
                border-radius: 5px;
                font-size: 14px;
            }}
            .controls {{
                background: #2a2a2a;
                padding: 15px;
                text-align: center;
            }}
            button {{
                background: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                margin: 0 5px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 14px;
            }}
            button:hover {{
                background: #45a049;
            }}
            .info {{
                background: #2a2a2a;
                padding: 15px;
                margin-top: 20px;
                border-radius: 8px;
            }}
        </style>
    </head>
    <body>
        <div class="video-container">
            <div style="position: relative;">
                <video id="videoPlayer" controls autoplay muted>
                    <source src="https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
                <div class="overlay">
                    <strong>Drone {drone_id}</strong><br>
                    <span style="color: #4CAF50;">● LIVE</span>
                </div>
            </div>
            <div class="controls">
                <button onclick="document.getElementById('videoPlayer').play()">Play</button>
                <button onclick="document.getElementById('videoPlayer').pause()">Pause</button>
                <button onclick="document.getElementById('videoPlayer').muted = !document.getElementById('videoPlayer').muted">
                    Mute/Unmute
                </button>
                <button onclick="window.location.href='/api/video/stream/{drone_id}'">Refresh Stream</button>
            </div>
        </div>
        <div class="info">
            <h3>Stream Information</h3>
            <p><strong>Drone ID:</strong> {drone_id}</p>
            <p><strong>Status:</strong> Streaming (Demo Mode)</p>
            <p><strong>Quality:</strong> 720p</p>
            <p><strong>Note:</strong> This is a demo video feed. In production, this would show the live camera feed from the drone.</p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)
