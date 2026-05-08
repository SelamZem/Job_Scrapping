// Visited jobs tracking using localStorage - works for all users (logged in or not)
const STORAGE_KEY = 'care_jobs_visited'

export const getVisitedJobs = () => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    return stored ? JSON.parse(stored) : []
  } catch (error) {
    console.error('Error reading visited jobs:', error)
    return []
  }
}

export const markJobVisited = (jobId) => {
  try {
    const visited = getVisitedJobs()
    if (!visited.includes(jobId)) {
      visited.push(jobId)
      localStorage.setItem(STORAGE_KEY, JSON.stringify(visited))
    }
    return { error: null, visited }
  } catch (error) {
    console.error('Error marking job visited:', error)
    return { error: 'Failed to mark job as visited', visited: getVisitedJobs() }
  }
}

export const isJobVisited = (jobId) => {
  return getVisitedJobs().includes(jobId)
}

export const clearVisitedJobs = () => {
  try {
    localStorage.removeItem(STORAGE_KEY)
    return { error: null, visited: [] }
  } catch (error) {
    console.error('Error clearing visited jobs:', error)
    return { error: 'Failed to clear visited jobs', visited: getVisitedJobs() }
  }
}
