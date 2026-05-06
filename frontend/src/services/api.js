import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

export const getJobs = async () => {
  const response = await axios.get(`${API_BASE_URL}/jobs/?limit=1000`)
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
