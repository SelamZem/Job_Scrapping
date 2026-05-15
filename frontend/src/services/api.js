import axios from 'axios'
import { getToken } from './auth'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

// Shared axios instance — attaches auth token to every request
const api = axios.create({ baseURL: API_BASE_URL })

api.interceptors.request.use((config) => {
  const token = getToken()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

export default api

export const getJobs = async (page = 1, limit = 12, search = '', location = '', tags = []) => {
  const startTime = performance.now()
  const skip = (page - 1) * limit
  const params = new URLSearchParams()
  params.append('skip', skip)
  params.append('limit', limit)
  if (search) params.append('search', search)
  if (location) params.append('location', location)
  if (Array.isArray(tags)) tags.forEach(t => params.append('tag', t))
  else if (tags) params.append('tag', tags)
  const response = await api.get(`/jobs/?${params.toString()}`)
  console.log(`🚀 getJobs took ${(performance.now() - startTime).toFixed(0)}ms`)
  return response.data
}

export const scrapeJobs = async (query, location) => {
  const response = await api.post('/jobs/scrape', { query, location })
  return response.data
}

export const getTags = async () => {
  const response = await api.get('/tags/')
  return response.data
}

export const getRecommendations = async (userProfile) => {
  const response = await api.post('/recommendations/', { user_profile: userProfile })
  return response.data
}

export const getCareerAdvice = async (jobTitle) => {
  const response = await api.get(`/recommendations/advice/${jobTitle}`)
  return response.data
}
