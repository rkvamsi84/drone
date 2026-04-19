import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import axios from 'axios'
import { ArrowLeft, MapPin, Package, Calendar, Clock, AlertCircle, CheckCircle, Play } from 'lucide-react'
import ReplayViewer from '../components/ReplayViewer'

const MissionDetails = () => {
  const { id } = useParams()
  const navigate = useNavigate()
  const [mission, setMission] = useState(null)
  const [loading, setLoading] = useState(true)
  const [showReplay, setShowReplay] = useState(false)

  useEffect(() => {
    fetchMission()
  }, [id])

  const fetchMission = async () => {
    try {
      const res = await axios.get(`/api/missions/${id}`)
      setMission(res.data)
    } catch (err) {
      console.error('Failed to fetch mission:', err)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      in_progress: 'bg-blue-100 text-blue-800 border-blue-300',
      completed: 'bg-green-100 text-green-800 border-green-300',
      failed: 'bg-red-100 text-red-800 border-red-300',
      cancelled: 'bg-gray-100 text-gray-800 border-gray-300',
    }
    return colors[status] || 'bg-gray-100 text-gray-800 border-gray-300'
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'Not started'
    return new Date(dateString).toLocaleString()
  }

  const formatDuration = (minutes) => {
    if (!minutes) return 'N/A'
    const hrs = Math.floor(minutes / 60)
    const mins = minutes % 60
    return `${hrs}h ${mins}m`
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!mission) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">Mission not found</p>
        <button
          onClick={() => navigate('/missions')}
          className="mt-4 text-primary-600 hover:text-primary-800"
        >
          Back to Missions
        </button>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <button
          onClick={() => navigate('/missions')}
          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <ArrowLeft className="h-6 w-6" />
        </button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold text-gray-900">{mission.name}</h1>
          <p className="text-gray-600 mt-2">{mission.description}</p>
        </div>
        <button
          onClick={() => setShowReplay(true)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Play className="h-5 w-5" />
          Replay Flight
        </button>
        <div className={`px-4 py-2 rounded-lg border-2 ${getStatusColor(mission.status)}`}>
          <span className="font-semibold">{mission.status.replace('_', ' ').toUpperCase()}</span>
        </div>
      </div>

      {showReplay && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <ReplayViewer missionId={mission.id} onClose={() => setShowReplay(false)} />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Info */}
        <div className="lg:col-span-2 space-y-6">
          {/* Mission Details */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Mission Details</h2>
            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <Package className="h-5 w-5 text-gray-400 mt-0.5" />
                <div>
                  <p className="text-sm text-gray-600">Mission ID</p>
                  <p className="font-medium text-gray-900">{mission.mission_id}</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Calendar className="h-5 w-5 text-gray-400 mt-0.5" />
                <div>
                  <p className="text-sm text-gray-600">Priority</p>
                  <p className="font-medium capitalize text-gray-900">{mission.priority}</p>
                </div>
              </div>
              <div className="flex items-start gap-3">
                <Clock className="h-5 w-5 text-gray-400 mt-0.5" />
                <div>
                  <p className="text-sm text-gray-600">Estimated Duration</p>
                  <p className="font-medium text-gray-900">{formatDuration(mission.estimated_duration)}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Route Info */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Route</h2>
            <div className="space-y-4">
              <div>
                <div className="flex items-center gap-2 text-green-600 mb-2">
                  <CheckCircle className="h-5 w-5" />
                  <span className="font-medium">Origin</span>
                </div>
                <p className="text-gray-900 font-medium">{mission.origin_name}</p>
                <p className="text-sm text-gray-600">{mission.origin_lat}, {mission.origin_lon}</p>
              </div>
              <div className="border-l-2 border-dashed border-gray-300 ml-2 pl-4">
                <MapPin className="h-4 w-4 text-gray-400 -ml-6 bg-white p-1" />
              </div>
              <div>
                <div className="flex items-center gap-2 text-primary-600 mb-2">
                  <MapPin className="h-5 w-5" />
                  <span className="font-medium">Destination</span>
                </div>
                <p className="text-gray-900 font-medium">{mission.dest_name}</p>
                <p className="text-sm text-gray-600">{mission.dest_lat}, {mission.dest_lon}</p>
              </div>
            </div>
          </div>

          {/* Payload Info */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Payload Information</h2>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-600">Weight</p>
                <p className="font-medium text-gray-900">{mission.payload_weight} kg</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Description</p>
                <p className="text-gray-900">{mission.payload_description}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Timeline */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Timeline</h2>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-gray-600">Created</p>
                <p className="font-medium text-gray-900">{formatDate(mission.created_at)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Started</p>
                <p className="font-medium text-gray-900">{formatDate(mission.started_at)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Completed</p>
                <p className="font-medium text-gray-900">{formatDate(mission.completed_at)}</p>
              </div>
            </div>
          </div>

          {/* Delivery Confirmation */}
          {mission.delivery_confirmation_code && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-6">
              <div className="flex items-center gap-2 text-green-700 mb-2">
                <CheckCircle className="h-5 w-5" />
                <span className="font-semibold">Confirmed</span>
              </div>
              <p className="text-sm text-gray-600">Confirmation Code</p>
              <p className="font-mono font-bold text-lg text-gray-900">{mission.delivery_confirmation_code}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default MissionDetails
