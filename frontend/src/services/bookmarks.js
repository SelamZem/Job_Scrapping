// Bookmark service — uses server-side storage when logged in, localStorage as fallback
import axios from 'axios'
import { isAuthenticated, getToken } from './auth'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

// Axios instance with auth header
const authAxios = () =>
  axios.create({
    baseURL: API_BASE_URL,
    headers: { Authorization: `Bearer ${getToken()}` },
  })

// ─── localStorage fallback (unauthenticated) ────────────────────────────────

const LOCAL_KEY = 'care_jobs_bookmarks_guest'

const getLocalBookmarks = () => {
  try {
    return JSON.parse(localStorage.getItem(LOCAL_KEY) || '[]')
  } catch {
    return []
  }
}

const setLocalBookmarks = (ids) => {
  localStorage.setItem(LOCAL_KEY, JSON.stringify(ids))
}

// ─── Public API ──────────────────────────────────────────────────────────────

export const canBookmark = () => true // anyone can bookmark; server requires auth

/**
 * Fetch all saved job IDs.
 * Returns an array of integers.
 */
export const getBookmarks = async () => {
  if (!isAuthenticated()) return getLocalBookmarks()
  try {
    const res = await authAxios().get('/bookmarks/')
    return res.data // array of job IDs
  } catch {
    return getLocalBookmarks()
  }
}

/**
 * Add a job to saved jobs.
 */
export const addBookmark = async (jobId) => {
  if (!isAuthenticated()) {
    const ids = getLocalBookmarks()
    if (!ids.includes(jobId)) {
      ids.push(jobId)
      setLocalBookmarks(ids)
    }
    return { error: null, bookmarks: ids }
  }
  try {
    const res = await authAxios().post(`/bookmarks/${jobId}`)
    return { error: null, bookmarks: res.data.saved_jobs }
  } catch (e) {
    return { error: 'Failed to save job', bookmarks: [] }
  }
}

/**
 * Remove a job from saved jobs.
 */
export const removeBookmark = async (jobId) => {
  if (!isAuthenticated()) {
    const ids = getLocalBookmarks().filter((id) => id !== jobId)
    setLocalBookmarks(ids)
    return { error: null, bookmarks: ids }
  }
  try {
    const res = await authAxios().delete(`/bookmarks/${jobId}`)
    return { error: null, bookmarks: res.data.saved_jobs }
  } catch (e) {
    return { error: 'Failed to remove job', bookmarks: [] }
  }
}

/**
 * Check if a single job is bookmarked (sync, uses cached state).
 * Pass the bookmarkedIds array fetched via getBookmarks() for accuracy.
 */
export const isBookmarked = (jobId, bookmarkedIds = []) => {
  if (bookmarkedIds.length > 0) return bookmarkedIds.includes(jobId)
  // fallback: check localStorage for guests
  return getLocalBookmarks().includes(jobId)
}

/**
 * Toggle bookmark state for a job.
 */
export const toggleBookmark = async (jobId, currentlyBookmarked) => {
  if (currentlyBookmarked) {
    const result = await removeBookmark(jobId)
    return { ...result, isBookmarked: false }
  } else {
    const result = await addBookmark(jobId)
    return { ...result, isBookmarked: true }
  }
}
