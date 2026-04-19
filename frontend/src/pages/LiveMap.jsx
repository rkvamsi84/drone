import { useState, useEffect } from 'react'
import { MapContainer, TileLayer, Marker, Popup, Polyline, Circle } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'
import axios from 'axios'
import { Plane, Battery, Activity, MapPin, Package, Clock, TrendingUp } from 'lucide-react'

// Fix for default marker icons in production
delete L.Icon.Default.prototype._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
})

const LiveMap = () => {
  const [drones, setDrones] = useState([])
  const [missions, setMissions] = useState([])
  const [telemetry, setTelemetry] = useState({})
  const [selectedDrone, setSelectedDrone] = useState(null)

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 5000) // Update every 5 seconds
    return () => clearInterval(interval)
  }, [])

  const fetchData = async () => {
    try {
      const [dronesRes, missionsRes] = await Promise.all([
        axios.get('/api/drones'),
        axios.get('/api/missions?status=in_progress')
      ])
      setDrones(dronesRes.data)
      setMissions(missionsRes.data)

      // Fetch telemetry for each drone
      const telemetryData = {}
      for (const drone of dronesRes.data) {
        try {
          const telemetryRes = await axios.get(`/api/telemetry/drones/${drone.id}/latest`)
          telemetryData[drone.id] = telemetryRes.data
        } catch (err) {
          console.error(`Failed to fetch telemetry for drone ${drone.id}`)
        }
      }
      setTelemetry(telemetryData)
    } catch (err) {
      console.error('Failed to fetch data:', err)
    }
  }

  const getDroneIcon = (status, batteryLevel) => {
    const color = batteryLevel > 30 ? '#10b981' : batteryLevel > 10 ? '#f59e0b' : '#ef4444'
    return L.divIcon({
      className: 'custom-marker',
      html: `<div style="background-color: ${color}; width: 24px; height: 24px; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></div>`,
      iconSize: [24, 24]
    })
  }

  const getMissionRoute = (mission) => {
    if (!mission || !telemetry[mission.drone_id]) return []
    return [
      [mission.origin_lat, mission.origin_lon],
      [mission.dest_lat, mission.dest_lon]
    ]
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Live Map</h1>
        <p className="text-gray-600 mt-2">Real-time drone tracking and mission visualization</p>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        <MapContainer
          center={[28.6139, 77.2090]}
          zoom={11}
          style={{ height: '600px', width: '100%' }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {/* Draw mission routes */}
          {missions.map((mission) => {
            const route = getMissionRoute(mission)
            return (
              <div key={mission.id}>
                {route.length > 0 && (
                  <Polyline
                    positions={route}
                    color="#3b82f6"
                    weight={2}
                    dashArray="5, 5"
                  />
                )}
              </div>
            )
          })}

          {/* Origin markers */}
          {missions.map((mission) => (
            <Marker
              key={`origin-${mission.id}`}
              position={[mission.origin_lat, mission.origin_lon]}
              icon={L.icon({
                iconUrl: 'data:image/svg+xml;base64,' + btoa(`
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="#10b981">
                    <circle cx="12" cy="12" r="8"/>
                  </svg>
                `),
                iconSize: [24, 24]
              })}
            >
              <Popup>
                <div>
                  <strong>Origin:</strong> {mission.origin_name}
                </div>
              </Popup>
            </Marker>
          ))}

          {/* Destination markers */}
          {missions.map((mission) => (
            <Marker
              key={`dest-${mission.id}`}
              position={[mission.dest_lat, mission.dest_lon]}
              icon={L.icon({
                iconUrl: 'data:image/svg+xml;base64,' + btoa(`
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="#3b82f6">
                    <circle cx="12" cy="12" r="8"/>
                  </svg>
                `),
                iconSize: [24, 24]
              })}
            >
              <Popup>
                <div>
                  <strong>Destination:</strong> {mission.dest_name}
                </div>
              </Popup>
            </Marker>
          ))}

          {/* Drone markers */}
          {Object.entries(telemetry).map(([droneId, data]) => {
            const drone = drones.find(d => d.id === parseInt(droneId))
            if (!drone) return null

            return (
              <Marker
                key={`drone-${droneId}`}
                position={[data.latitude, data.longitude]}
                icon={getDroneIcon(drone.status, data.battery_percent)}
              >
                <Popup>
                  <div className="space-y-1">
                    <div className="font-bold">{drone.name}</div>
                    <div className="text-sm">
                      <div>Status: {drone.status}</div>
                      <div>Battery: {data.battery_percent.toFixed(0)}%</div>
                      <div>Altitude: {data.altitude.toFixed(0)}m</div>
                      <div>Speed: {data.speed.toFixed(1)} m/s</div>
                      <div>Heading: {data.heading.toFixed(0)}°</div>
                    </div>
                  </div>
                </Popup>
              </Marker>
            )
          })}
        </MapContainer>
      </div>

      {/* Detailed Statistics Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Active Drones</p>
              <p className="text-2xl font-bold text-gray-900">{drones.filter(d => d.status === 'flying').length}</p>
            </div>
            <div className="p-3 bg-blue-100 rounded-lg">
              <Plane className="h-6 w-6 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Active Missions</p>
              <p className="text-2xl font-bold text-gray-900">{missions.length}</p>
            </div>
            <div className="p-3 bg-green-100 rounded-lg">
              <Package className="h-6 w-6 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Avg Battery</p>
              <p className="text-2xl font-bold text-gray-900">
                {drones.length > 0 
                  ? Math.round(drones.reduce((sum, d) => sum + d.battery_level, 0) / drones.length)
                  : 0}%
              </p>
            </div>
            <div className="p-3 bg-yellow-100 rounded-lg">
              <Battery className="h-6 w-6 text-yellow-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600">Total Drones</p>
              <p className="text-2xl font-bold text-gray-900">{drones.length}</p>
            </div>
            <div className="p-3 bg-purple-100 rounded-lg">
              <Activity className="h-6 w-6 text-purple-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Drone Status Panel with Details */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {drones.map((drone) => {
          const droneTelemetry = telemetry[drone.id]
          return (
            <div 
              key={drone.id} 
              className={`bg-white rounded-lg shadow-sm border-2 p-4 cursor-pointer transition-all ${
                selectedDrone === drone.id ? 'border-blue-500 shadow-lg' : 'border-gray-200'
              }`}
              onClick={() => setSelectedDrone(selectedDrone === drone.id ? null : drone.id)}
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Plane className={`h-5 w-5 ${drone.status === 'flying' ? 'text-blue-600' : 'text-gray-400'}`} />
                  <h3 className="font-semibold text-gray-900">{drone.name}</h3>
                </div>
                <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                  drone.status === 'flying' ? 'bg-blue-100 text-blue-800' :
                  drone.status === 'idle' ? 'bg-gray-100 text-gray-800' :
                  'bg-yellow-100 text-yellow-800'
                }`}>
                  {drone.status}
                </span>
              </div>

              {/* Battery Indicator */}
              <div className="mb-3">
                <div className="flex items-center justify-between text-sm mb-1">
                  <span className="text-gray-600 flex items-center gap-1">
                    <Battery className="h-4 w-4" />
                    Battery
                  </span>
                  <span className={`font-semibold ${
                    drone.battery_level > 60 ? 'text-green-600' :
                    drone.battery_level > 30 ? 'text-yellow-600' :
                    'text-red-600'
                  }`}>
                    {drone.battery_level.toFixed(0)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full transition-all ${
                      drone.battery_level > 60 ? 'bg-green-500' :
                      drone.battery_level > 30 ? 'bg-yellow-500' :
                      'bg-red-500'
                    }`}
                    style={{ width: `${drone.battery_level}%` }}
                  ></div>
                </div>
              </div>

              {droneTelemetry ? (
                <div className="space-y-2 text-sm">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600 flex items-center gap-1">
                      <MapPin className="h-4 w-4" />
                      Position
                    </span>
                    <span className="font-mono text-xs">{droneTelemetry.latitude.toFixed(4)}, {droneTelemetry.longitude.toFixed(4)}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600 flex items-center gap-1">
                      <TrendingUp className="h-4 w-4" />
                      Altitude
                    </span>
                    <span className="font-semibold">{droneTelemetry.altitude.toFixed(0)}m</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">Speed</span>
                    <span className="font-semibold">{droneTelemetry.speed.toFixed(1)} m/s</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">Heading</span>
                    <span className="font-semibold">{droneTelemetry.heading.toFixed(0)}°</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">GPS Fix</span>
                    <span className="font-semibold">{droneTelemetry.satellites} sats</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">Mode</span>
                    <span className="font-semibold">{droneTelemetry.flight_mode}</span>
                  </div>
                </div>
              ) : (
                <div className="text-center py-4 text-gray-400 text-sm">
                  <Clock className="h-8 w-8 mx-auto mb-2" />
                  No telemetry data
                </div>
              )}
            </div>
          )
        })}
      </div>

      {drones.length === 0 && (
        <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
          <Plane className="h-12 w-12 mx-auto text-gray-400 mb-4" />
          <p className="text-gray-500">No drones in fleet yet</p>
        </div>
      )}
    </div>
  )
}

export default LiveMap
