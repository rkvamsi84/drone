import { useState, useEffect } from 'react'
import axios from 'axios'
import { Play, Pause, SkipBack, SkipForward, Clock } from 'lucide-react'

const ReplayViewer = ({ missionId, onClose }) => {
  const [telemetryData, setTelemetryData] = useState([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [speed, setSpeed] = useState(1)

  useEffect(() => {
    fetchTelemetry()
  }, [missionId])

  const fetchTelemetry = async () => {
    try {
      const res = await axios.get(`/api/replay/mission/${missionId}`)
      setTelemetryData(res.data)
    } catch (err) {
      console.error('Failed to fetch telemetry:', err)
    }
  }

  useEffect(() => {
    if (!isPlaying || telemetryData.length === 0) return

    const interval = setInterval(() => {
      setCurrentIndex(prev => {
        if (prev >= telemetryData.length - 1) {
          setIsPlaying(false)
          return prev
        }
        return prev + 1
      })
    }, 1000 / speed)

    return () => clearInterval(interval)
  }, [isPlaying, speed, telemetryData.length])

  const currentTelemetry = telemetryData[currentIndex]

  const handlePlay = () => {
    setIsPlaying(true)
  }

  const handlePause = () => {
    setIsPlaying(false)
  }

  const handlePrevious = () => {
    setCurrentIndex(Math.max(0, currentIndex - 1))
  }

  const handleNext = () => {
    setCurrentIndex(Math.min(telemetryData.length - 1, currentIndex + 1))
  }

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString()
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Flight Replay</h2>
        <button
          onClick={onClose}
          className="text-gray-500 hover:text-gray-700"
        >
          ✕
        </button>
      </div>

      {currentTelemetry && (
        <>
          {/* Control Panel */}
          <div className="bg-gray-50 rounded-lg p-4 mb-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-4">
                <button
                  onClick={handlePrevious}
                  className="p-2 rounded hover:bg-gray-200"
                  disabled={currentIndex === 0}
                >
                  <SkipBack className="h-5 w-5" />
                </button>
                
                {isPlaying ? (
                  <button onClick={handlePause} className="p-2 rounded hover:bg-gray-200">
                    <Pause className="h-5 w-5" />
                  </button>
                ) : (
                  <button onClick={handlePlay} className="p-2 rounded hover:bg-gray-200">
                    <Play className="h-5 w-5" />
                  </button>
                )}
                
                <button
                  onClick={handleNext}
                  className="p-2 rounded hover:bg-gray-200"
                  disabled={currentIndex >= telemetryData.length - 1}
                >
                  <SkipForward className="h-5 w-5" />
                </button>
              </div>

              <div className="flex items-center gap-4">
                <span className="text-sm text-gray-600">
                  {currentIndex + 1} / {telemetryData.length}
                </span>
                <select
                  value={speed}
                  onChange={(e) => setSpeed(parseFloat(e.target.value))}
                  className="px-3 py-1 border border-gray-300 rounded"
                >
                  <option value="0.5">0.5x</option>
                  <option value="1">1x</option>
                  <option value="2">2x</option>
                  <option value="4">4x</option>
                </select>
              </div>
            </div>

            <div className="flex items-center gap-2 text-sm text-gray-600">
              <Clock className="h-4 w-4" />
              <span>{formatTime(currentTelemetry.timestamp)}</span>
            </div>

            {/* Progress Bar */}
            <div className="mt-4">
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all"
                  style={{ width: `${((currentIndex + 1) / telemetryData.length) * 100}%` }}
                ></div>
              </div>
            </div>
          </div>

          {/* Telemetry Display */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <div className="text-sm text-gray-600">Position</div>
              <div className="font-mono text-sm font-semibold">
                {currentTelemetry.latitude.toFixed(6)}, {currentTelemetry.longitude.toFixed(6)}
              </div>
            </div>

            <div className="bg-green-50 p-4 rounded-lg">
              <div className="text-sm text-gray-600">Altitude</div>
              <div className="text-2xl font-bold text-green-700">
                {currentTelemetry.altitude.toFixed(0)}m
              </div>
            </div>

            <div className="bg-yellow-50 p-4 rounded-lg">
              <div className="text-sm text-gray-600">Battery</div>
              <div className="text-2xl font-bold text-yellow-700">
                {currentTelemetry.battery_percent.toFixed(0)}%
              </div>
            </div>

            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="text-sm text-gray-600">Speed</div>
              <div className="text-2xl font-bold text-purple-700">
                {currentTelemetry.speed.toFixed(1)} m/s
              </div>
            </div>

            <div className="bg-indigo-50 p-4 rounded-lg">
              <div className="text-sm text-gray-600">Heading</div>
              <div className="text-2xl font-bold text-indigo-700">
                {currentTelemetry.heading.toFixed(0)}°
              </div>
            </div>

            <div className="bg-cyan-50 p-4 rounded-lg">
              <div className="text-sm text-gray-600">GPS Fix</div>
              <div className="text-2xl font-bold text-cyan-700">
                {currentTelemetry.satellites} sats
              </div>
            </div>

            <div className="bg-orange-50 p-4 rounded-lg">
              <div className="text-sm text-gray-600">Flight Mode</div>
              <div className="text-lg font-semibold text-orange-700">
                {currentTelemetry.flight_mode}
              </div>
            </div>

            <div className="bg-red-50 p-4 rounded-lg">
              <div className="text-sm text-gray-600">Status</div>
              <div className="text-lg font-semibold">
                {currentTelemetry.is_airborne ? 'Airborne' : 'On Ground'}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default ReplayViewer
