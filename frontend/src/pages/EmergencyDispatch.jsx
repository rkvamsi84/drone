import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import { AlertTriangle, MapPin, Package, Send } from 'lucide-react'

const EmergencyDispatch = () => {
  const navigate = useNavigate()
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    origin_lat: '',
    origin_lon: '',
    origin_name: '',
    dest_lat: '',
    dest_lon: '',
    dest_name: '',
    payload_weight: '',
    payload_description: '',
    min_temperature: '',
    max_temperature: ''
  })
  const [availableDrones, setAvailableDrones] = useState([])
  const [dispatching, setDispatching] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetchAvailableDrones()
  }, [])

  const fetchAvailableDrones = async () => {
    try {
      const res = await axios.get('/api/drones')
      const available = res.data.filter(d => 
        d.status === 'idle' && d.battery_level > 50
      )
      setAvailableDrones(available)
    } catch (err) {
      setError('Failed to fetch available drones')
    }
  }

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setDispatching(true)
    setError(null)

    try {
      const payload = {
        name: formData.name,
        description: formData.description,
        origin_lat: parseFloat(formData.origin_lat),
        origin_lon: parseFloat(formData.origin_lon),
        origin_name: formData.origin_name,
        dest_lat: parseFloat(formData.dest_lat),
        dest_lon: parseFloat(formData.dest_lon),
        dest_name: formData.dest_name,
        payload_weight: parseFloat(formData.payload_weight),
        payload_description: formData.payload_description,
        min_temperature: formData.min_temperature ? parseFloat(formData.min_temperature) : null,
        max_temperature: formData.max_temperature ? parseFloat(formData.max_temperature) : null,
        priority: 'emergency'
      }

      await axios.post('/api/emergency/dispatch', payload)
      navigate('/missions')
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to dispatch emergency mission')
    } finally {
      setDispatching(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="bg-red-50 border-l-4 border-red-500 p-4">
        <div className="flex items-center">
          <AlertTriangle className="h-6 w-6 text-red-600 mr-3" />
          <div>
            <h1 className="text-2xl font-bold text-red-900">Emergency SOS Dispatch</h1>
            <p className="text-red-700">Rapid medical delivery for critical situations</p>
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {availableDrones.length === 0 && (
        <div className="bg-yellow-50 border border-yellow-400 text-yellow-700 px-4 py-3 rounded">
          ⚠️ No available drones with sufficient battery (&gt;50%) for emergency dispatch
        </div>
      )}

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Mission Name *
            </label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
              placeholder="Emergency medicine delivery"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description *
            </label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              required
              rows="3"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
              placeholder="Critical medical supplies needed immediately"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center">
                <MapPin className="h-4 w-4 mr-1" />
                Origin Lat *
              </label>
              <input
                type="number"
                step="0.00001"
                name="origin_lat"
                value={formData.origin_lat}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center">
                <MapPin className="h-4 w-4 mr-1" />
                Origin Lon *
              </label>
              <input
                type="number"
                step="0.00001"
                name="origin_lon"
                value={formData.origin_lon}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Origin Name *
            </label>
            <input
              type="text"
              name="origin_name"
              value={formData.origin_name}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
              placeholder="Base Hospital"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center">
                <MapPin className="h-4 w-4 mr-1" />
                Destination Lat *
              </label>
              <input
                type="number"
                step="0.00001"
                name="dest_lat"
                value={formData.dest_lat}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center">
                <MapPin className="h-4 w-4 mr-1" />
                Destination Lon *
              </label>
              <input
                type="number"
                step="0.00001"
                name="dest_lon"
                value={formData.dest_lon}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Destination Name *
            </label>
            <input
              type="text"
              name="dest_name"
              value={formData.dest_name}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
              placeholder="Emergency Location"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2 flex items-center">
                <Package className="h-4 w-4 mr-1" />
                Payload Weight (kg) *
              </label>
              <input
                type="number"
                step="0.1"
                name="payload_weight"
                value={formData.payload_weight}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Payload Description *
            </label>
            <textarea
              name="payload_description"
              value={formData.payload_description}
              onChange={handleChange}
              required
              rows="2"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
              placeholder="Emergency medicines, insulin, blood samples..."
            />
          </div>

          <div className="bg-blue-50 border border-blue-200 p-4 rounded-md">
            <h3 className="font-semibold text-blue-900 mb-2">Cold-Chain Compliance (Optional)</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-blue-700 mb-1">
                  Min Temperature (°C)
                </label>
                <input
                  type="number"
                  step="0.1"
                  name="min_temperature"
                  value={formData.min_temperature}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-blue-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-blue-700 mb-1">
                  Max Temperature (°C)
                </label>
                <input
                  type="number"
                  step="0.1"
                  name="max_temperature"
                  value={formData.max_temperature}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-blue-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          </div>

          <div className="flex gap-4">
            <button
              type="submit"
              disabled={dispatching || availableDrones.length === 0}
              className="flex items-center gap-2 bg-red-600 text-white px-6 py-3 rounded-lg hover:bg-red-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              <Send className="h-5 w-5" />
              {dispatching ? 'Dispatching...' : 'Dispatch Emergency Mission'}
            </button>
            <button
              type="button"
              onClick={() => navigate('/missions')}
              className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default EmergencyDispatch
