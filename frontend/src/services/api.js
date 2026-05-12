import axios from 'axios'
import { getToken } from './auth'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

// Create axios instance for default export
const api = axios.create({
  baseURL: API_BASE_URL
})

// Add auth token to all requests
api.interceptors.request.use((config) => {
  const token = getToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default api

export const getJobs = async (page = 1, limit = 12, search = '', location = '', tag = '') => {
  const startTime = performance.now()
  const skip = (page - 1) * limit
  const params = new URLSearchParams()
  params.append('skip', skip)
  params.append('limit', limit)
  if (search) params.append('search', search)
  if (location) params.append('location', location)
  if (tag) params.append('tag', tag)
  
  const response = await axios.get(`${API_BASE_URL}/jobs/?${params.toString()}`)
  const endTime = performance.now()
  const duration = endTime - startTime
  
  console.log(`🚀 Frontend: getJobs took ${duration.toFixed(2)}ms`)
  return response.data
}

export const scrapeJobs = async (query, location) => {
  const response = await axios.post(`${API_BASE_URL}/jobs/scrape`, {
    query,
    location
  })
  return response.data
}

export const getTags = async () => {
  const response = await axios.get(`${API_BASE_URL}/tags/`)
  return response.data
}

export const getRecommendations = async (userProfile) => {
  const response = await axios.post(`${API_BASE_URL}/recommendations/`, {
    user_profile: userProfile
  })
  return response.data
}

export const getCareerAdvice = async (jobTitle) => {
  const response = await axios.get(`${API_BASE_URL}/recommendations/advice/${jobTitle}`)
  return response.data
}
