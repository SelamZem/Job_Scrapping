// Bookmark service — uses server-side storage when logged in, localStorage as fallback
import api from './api'
import { isAuthenticated } from './auth'

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

export const getBookmarks = async () => {
  if (!isAuthenticated()) return getLocalBookmarks()
  try {
    const res = await api.get('/bookmarks/')
    return res.data
  } catch {
    return getLocalBookmarks()
  }
}

export const addBookmark = async (jobId) => {
  if (!isAuthenticated()) {
    const ids = getLocalBookmarks()
    if (!ids.includes(jobId)) { ids.push(jobId); setLocalBookmarks(ids) }
    return { error: null, bookmarks: ids }
  }
  try {
    const res = await api.post(`/bookmarks/${jobId}`)
    return { error: null, bookmarks: res.data.saved_jobs }
  } catch (e) {
    return { error: 'Failed to save job', bookmarks: [] }
  }
}

export const removeBookmark = async (jobId) => {
  if (!isAuthenticated()) {
    const ids = getLocalBookmarks().filter((id) => id !== jobId)
    setLocalBookmarks(ids)
    return { error: null, bookmarks: ids }
  }
  try {
    const res = await api.delete(`/bookmarks/${jobId}`)
    return { error: null, bookmarks: res.data.saved_jobs }
  } catch (e) {
    return { error: 'Failed to remove job', bookmarks: [] }
  }
}

export const isBookmarked = (jobId, bookmarkedIds = []) => {
  if (bookmarkedIds.length > 0) return bookmarkedIds.includes(jobId)
  return getLocalBookmarks().includes(jobId)
}

export const toggleBookmark = async (jobId, currentlyBookmarked) => {
  if (currentlyBookmarked) {
    const result = await removeBookmark(jobId)
    return { ...result, isBookmarked: false }
  } else {
    const result = await addBookmark(jobId)
    return { ...result, isBookmarked: true }
  }
}
