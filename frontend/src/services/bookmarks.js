// Bookmark service using localStorage - requires authentication
import { isAuthenticated, getUserInfo } from './auth'

const getStorageKey = () => {
  const user = getUserInfo()
  if (!user || !user.id) return null
  return `care_jobs_bookmarks_${user.id}`
}

export const canBookmark = () => {
  return isAuthenticated() && getStorageKey() !== null
}

export const getBookmarks = () => {
  if (!canBookmark()) return []
  
  try {
    const key = getStorageKey()
    const stored = localStorage.getItem(key)
    return stored ? JSON.parse(stored) : []
  } catch (error) {
    console.error('Error reading bookmarks:', error)
    return []
  }
}

export const addBookmark = (jobId) => {
  if (!canBookmark()) {
    return { error: 'Please log in to save jobs', bookmarks: [] }
  }
  
  try {
    const bookmarks = getBookmarks()
    if (!bookmarks.includes(jobId)) {
      bookmarks.push(jobId)
      localStorage.setItem(getStorageKey(), JSON.stringify(bookmarks))
    }
    return { error: null, bookmarks }
  } catch (error) {
    console.error('Error adding bookmark:', error)
    return { error: 'Failed to save job', bookmarks: getBookmarks() }
  }
}

export const removeBookmark = (jobId) => {
  if (!canBookmark()) {
    return { error: 'Please log in to manage saved jobs', bookmarks: [] }
  }
  
  try {
    const bookmarks = getBookmarks().filter(id => id !== jobId)
    localStorage.setItem(getStorageKey(), JSON.stringify(bookmarks))
    return { error: null, bookmarks }
  } catch (error) {
    console.error('Error removing bookmark:', error)
    return { error: 'Failed to remove job', bookmarks: getBookmarks() }
  }
}

export const isBookmarked = (jobId) => {
  if (!canBookmark()) return false
  return getBookmarks().includes(jobId)
}

export const toggleBookmark = (jobId) => {
  if (!canBookmark()) {
    return { error: 'Please log in to save jobs', bookmarks: [], isBookmarked: false }
  }
  
  if (isBookmarked(jobId)) {
    const result = removeBookmark(jobId)
    return { ...result, isBookmarked: false }
  } else {
    const result = addBookmark(jobId)
    return { ...result, isBookmarked: true }
  }
}
