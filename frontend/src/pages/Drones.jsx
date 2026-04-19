import { useState, useEffect } from 'react'
import axios from 'axios'
import { Battery, Activity, Plus, X, Video } from 'lucide-react'
import LiveVideoStream from '../components/LiveVideoStream'

const Drones = () => {
  const [drones, setDrones] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [showVideo, setShowVideo] = useState(false)
  const [selectedDrone, setSelectedDrone] = useState(null)
  const [formData, setFormData] = useState({
    drone_id: '',
    name: '',
    model: '',
    firmware_version: ''
  })
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    fetchDrones()
    // Poll for updates every 5 seconds
    const interval = setInterval(fetchDrones, 5000)
    return () => clearInterval(interval)
  }, [])

  const fetchDrones = async () => {
    try {
      const res = await axios.get('/api/drones')
      setDrones(res.data)
    } catch (err) {
      console.error('Failed to fetch drones:', err)
    } finally {
      setLoading(false)
    }
  }

  const getStatusColor = (status) => {
    const colors = {
      idle: 'bg-gray-100 text-gray-800',
      flying: 'bg-blue-100 text-blue-800',
      landing: 'bg-yellow-100 text-yellow-800',
      maintenance: 'bg-orange-100 text-orange-800',
      error: 'bg-red-100 text-red-800',
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  const getBatteryColor = (level) => {
    if (level > 60) return 'text-green-600'
    if (level > 30) return 'text-yellow-600'
    return 'text-red-600'
  }

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    
    try {
      const payload = {
        drone_id: formData.drone_id,
        name: formData.name,
        model: formData.model,
        firmware_version: formData.firmware_version
      }
      
      await axios.post('/api/drones', payload)
      setShowForm(false)
      setFormData({
        drone_id: '',
        name: '',
        model: '',
        firmware_version: ''
      })
      fetchDrones()
    } catch (err) {
      console.error('Failed to create drone:', err)
      alert(err.response?.data?.detail || 'Failed to create drone. Please check all fields.')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Drones</h1>
          <p className="text-gray-600 mt-2">Monitor your drone fleet</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="flex items-center gap-2 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition-colors"
        >
          <Plus className="h-5 w-5" />
          Add Drone
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {drones.map((drone) => (
          <div key={drone.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">{drone.name}</h3>
                <p className="text-sm text-gray-500">{drone.drone_id}</p>
              </div>
              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(drone.status)}`}>
                {drone.status}
              </span>
            </div>

            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Battery</span>
                <span className={`flex items-center gap-1 text-sm font-semibold ${getBatteryColor(drone.battery_level)}`}>
                  <Battery className="h-4 w-4" />
                  {drone.battery_level.toFixed(0)}%
                </span>
              </div>

              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${getBatteryColor(drone.battery_level)}`}
                  style={{ width: `${drone.battery_level}%` }}
                ></div>
              </div>

              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Model</span>
                <span className="font-medium">{drone.model}</span>
              </div>

              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Hardware</span>
                <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                  drone.hardware_status === 'ok' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                }`}>
                  <Activity className="h-3 w-3 mr-1" />
                  {drone.hardware_status}
                </span>
              </div>

              {/* Watch Live Video Button */}
              <button
                onClick={() => {
                  setSelectedDrone(drone)
                  setShowVideo(true)
                }}
                className="w-full mt-3 flex items-center justify-center gap-2 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg transition-colors"
              >
                <Video className="h-4 w-4" />
                Watch Live Feed
              </button>
            </div>
          </div>
        ))}
      </div>

      {drones.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">No drones registered yet</p>
        </div>
      )}

      {/* Drone Creation Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center p-6 border-b border-gray-200">
              <h2 className="text-2xl font-bold text-gray-900">Add New Drone</h2>
              <button
                onClick={() => setShowForm(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-6 w-6" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Drone ID *
                </label>
                <input
                  type="text"
                  name="drone_id"
                  value={formData.drone_id}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="DRONE-004"
                />
                <p className="mt-1 text-xs text-gray-500">Unique identifier for the drone</p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Drone Name *
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="Himalayan Medical Drone 4"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Model *
                </label>
                <input
                  type="text"
                  name="model"
                  value={formData.model}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="VTOL Hybrid Long Range"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Firmware Version *
                </label>
                <input
                  type="text"
                  name="firmware_version"
                  value={formData.firmware_version}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="1.0.0"
                />
              </div>

              <div className="flex gap-4 pt-4">
                <button
                  type="submit"
                  disabled={submitting}
                  className="flex-1 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition-colors disabled:bg-gray-400"
                >
                  {submitting ? 'Adding...' : 'Add Drone'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Live Video Stream Modal */}
      {showVideo && selectedDrone && (
        <LiveVideoStream
          droneId={selectedDrone.id}
          droneName={selectedDrone.name}
          onClose={() => {
            setShowVideo(false)
            setSelectedDrone(null)
          }}
        />
      )}
    </div>
  )
}

export default Drones
