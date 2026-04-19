import { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import { Video, VideoOff, RefreshCw, Maximize2, Minimize2 } from 'lucide-react'

const LiveVideoStream = ({ droneId, droneName, onClose }) => {
  const [isStreaming, setIsStreaming] = useState(false)
  const [streamInfo, setStreamInfo] = useState(null)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [isMuted, setIsMuted] = useState(true)
  const videoRef = useRef(null)
  const containerRef = useRef(null)

  useEffect(() => {
    fetchStreamInfo()
  }, [droneId])

  const fetchStreamInfo = async () => {
    try {
      const res = await axios.get(`/api/video/stream/${droneId}`)
      setStreamInfo(res.data)
      startStream(res.data.stream_url)
    } catch (err) {
      console.error('Failed to fetch stream info:', err)
    }
  }

  const startStream = (streamUrl) => {
    // For demo, we'll use a mock video feed
    // In production, this would establish WebRTC connection
    const mockVideoUrl = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
    
    if (videoRef.current) {
      videoRef.current.src = mockVideoUrl
      setIsStreaming(true)
    }
  }

  const toggleFullscreen = () => {
    if (!isFullscreen) {
      if (containerRef.current.requestFullscreen) {
        containerRef.current.requestFullscreen()
      } else if (containerRef.current.webkitRequestFullscreen) {
        containerRef.current.webkitRequestFullscreen()
      }
      setIsFullscreen(true)
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen()
      } else if (document.webkitExitFullscreen) {
        document.webkitExitFullscreen()
      }
      setIsFullscreen(false)
    }
  }

  const toggleMute = () => {
    if (videoRef.current) {
      videoRef.current.muted = !videoRef.current.muted
      setIsMuted(videoRef.current.muted)
    }
  }

  const handleRefresh = () => {
    setIsStreaming(false)
    setTimeout(() => {
      fetchStreamInfo()
    }, 500)
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div ref={containerRef} className="bg-gray-900 rounded-lg shadow-2xl max-w-6xl w-full">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-700">
          <div className="flex items-center gap-3">
            <div className={`w-3 h-3 rounded-full ${isStreaming ? 'bg-red-500 animate-pulse' : 'bg-gray-500'}`}></div>
            <div>
              <h3 className="text-white font-semibold">{droneName || `Drone ${droneId}`} - Live Feed</h3>
              <p className="text-gray-400 text-sm">
                {isStreaming ? 'Streaming (Demo)' : 'Connecting...'}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={toggleFullscreen}
              className="p-2 text-gray-400 hover:text-white transition-colors"
              title="Fullscreen"
            >
              {isFullscreen ? <Minimize2 className="h-5 w-5" /> : <Maximize2 className="h-5 w-5" />}
            </button>
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-white transition-colors"
            >
              ✕
            </button>
          </div>
        </div>

        {/* Video Player */}
        <div className="relative bg-black">
          <video
            ref={videoRef}
            className="w-full h-auto max-h-[70vh]"
            controls
            autoPlay
            muted={isMuted}
            playsInline
          >
            <source src="https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4" type="video/mp4" />
            Your browser does not support the video tag.
          </video>
          
          {/* Overlay Info */}
          <div className="absolute top-4 left-4 bg-black bg-opacity-70 text-white p-3 rounded-lg">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
              <span className="text-sm font-semibold">LIVE</span>
            </div>
            <div className="text-xs mt-1 text-gray-300">
              Demo Stream • 720p
            </div>
          </div>
        </div>

        {/* Controls */}
        <div className="p-4 border-t border-gray-700 bg-gray-800">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <button
                onClick={toggleMute}
                className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors flex items-center gap-2"
              >
                {isMuted ? <VideoOff className="h-4 w-4" /> : <Video className="h-4 w-4" />}
                {isMuted ? 'Unmute' : 'Mute'}
              </button>
              <button
                onClick={handleRefresh}
                className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors flex items-center gap-2"
              >
                <RefreshCw className="h-4 w-4" />
                Refresh
              </button>
            </div>
            <div className="text-sm text-gray-400">
              Demo Mode - Sample video feed
            </div>
          </div>

          {/* Stream Info */}
          {streamInfo && (
            <div className="mt-4 p-3 bg-gray-900 rounded-lg">
              <p className="text-xs text-gray-400 mb-2">Stream Information:</p>
              <div className="grid grid-cols-2 gap-2 text-sm">
                <div>
                  <span className="text-gray-400">Status:</span>
                  <span className="text-green-400 ml-2">● Online</span>
                </div>
                <div>
                  <span className="text-gray-400">Quality:</span>
                  <span className="text-white ml-2">720p</span>
                </div>
                <div>
                  <span className="text-gray-400">Resolution:</span>
                  <span className="text-white ml-2">1280x720</span>
                </div>
                <div>
                  <span className="text-gray-400">FPS:</span>
                  <span className="text-white ml-2">30</span>
                </div>
              </div>
              <p className="text-xs text-yellow-400 mt-2">
                ⚠️ This is a demo stream. Production would show live drone camera feed via WebRTC.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default LiveVideoStream
