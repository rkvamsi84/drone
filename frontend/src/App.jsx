import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import PrivateRoute from './components/PrivateRoute'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Missions from './pages/Missions'
import Drones from './pages/Drones'
import MissionDetails from './pages/MissionDetails'
import LiveMap from './pages/LiveMap'
import FleetManagement from './pages/FleetManagement'
import EmergencyDispatch from './pages/EmergencyDispatch'
import Layout from './components/Layout'

function App() {
  return (
    <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route element={<PrivateRoute><Layout /></PrivateRoute>}>
            <Route path="/" element={<Dashboard />} />
            <Route path="/missions" element={<Missions />} />
            <Route path="/missions/:id" element={<MissionDetails />} />
            <Route path="/drones" element={<Drones />} />
            <Route path="/map" element={<LiveMap />} />
            <Route path="/fleet" element={<FleetManagement />} />
            <Route path="/emergency" element={<EmergencyDispatch />} />
          </Route>
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AuthProvider>
    </Router>
  )
}

export default App
