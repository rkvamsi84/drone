import { createContext, useContext, useState, useEffect } from 'react'
import axios from 'axios'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
      // Verify token is valid
      axios.get('/api/auth/me')
        .then(res => {
          setUser(res.data)
          setLoading(false)
        })
        .catch((err) => {
          // Silently handle 401 - user needs to login
          localStorage.removeItem('token')
          setToken(null)
          delete axios.defaults.headers.common['Authorization']
          setLoading(false)
        })
    } else {
      setLoading(false)
    }
  }, [token])

  const login = async (username, password) => {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)
    
    const res = await axios.post('/api/auth/login', formData)
    const { access_token } = res.data
    
    localStorage.setItem('token', access_token)
    setToken(access_token)
    axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
    
    const userRes = await axios.get('/api/auth/me')
    setUser(userRes.data)
    
    return userRes.data
  }

  const logout = () => {
    localStorage.removeItem('token')
    setToken(null)
    setUser(null)
    delete axios.defaults.headers.common['Authorization']
  }

  const register = async (username, email, password, fullName) => {
    await axios.post('/api/auth/register', {
      username,
      email,
      password,
      full_name: fullName,
      role: 'operator'
    })
  }

  return (
    <AuthContext.Provider value={{ user, token, login, logout, register, loading }}>
      {children}
    </AuthContext.Provider>
  )
}
