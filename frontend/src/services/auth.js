import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

export const signup = async (email, username, password) => {
  const response = await axios.post(`${API_BASE_URL}/auth/signup`, {
    email,
    username,
    password
  })
  return response.data
}

export const login = async (email, password) => {
  const response = await axios.post(`${API_BASE_URL}/auth/login`, {
    email,
    password
  })
  if (response.data.access_token) {
    localStorage.setItem('token', response.data.access_token)
  }
  return response.data
}

export const logout = () => {
  localStorage.removeItem('token')
}

export const getToken = () => {
  return localStorage.getItem('token')
}

export const isAuthenticated = () => {
  return !!getToken()
}

export const getUserInfo = () => {
  const token = getToken()
  if (!token) return null
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    return { email: payload.email, id: payload.sub }
  } catch {
    return null
  }
}
