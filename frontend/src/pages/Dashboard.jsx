import { useState, useEffect } from 'react'
import { Search, Filter, Briefcase, Sparkles, User, LogOut, LogIn, UserPlus, Heart, Moon, Sun, Shield } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import JobCard from '../components/JobCard'
import SearchBar from '../components/SearchBar'
import TagFilter from '../components/TagFilter'
import AIRecommendations from '../components/AIRecommendations'
import { getJobs, scrapeJobs, getTags } from '../services/api'
import { isAuthenticated, logout, getUserInfo, isAdmin } from '../services/auth'
import { getBookmarks } from '../services/bookmarks'
import { useDarkMode } from '../context/DarkModeContext'

function Dashboard() {
  const [jobs, setJobs] = useState([])
  const [totalJobs, setTotalJobs] = useState(0)
  const [tags, setTags] = useState([])
  const [selectedTags, setSelectedTags] = useState([])
  const [loading, setLoading] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [location, setLocation] = useState('')
  const [showRecommendations, setShowRecommendations] = useState(false)
  const [showSavedJobs, setShowSavedJobs] = useState(false)
  const [showProfileMenu, setShowProfileMenu] = useState(false)
  const [currentPage, setCurrentPage] = useState(1)
  const jobsPerPage = 12
  const navigate = useNavigate()
  const { isDark, toggleDark } = useDarkMode()

  // Load jobs when page or filters change
  useEffect(() => {
    loadJobs(currentPage, searchQuery, location, selectedTags[0] || '')
  }, [currentPage, searchQuery, location, selectedTags])

  // Close profile menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (showProfileMenu && !event.target.closest('.profile-menu-container')) {
        setShowProfileMenu(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [showProfileMenu])

  // Initial load
  useEffect(() => {
    loadTags()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const loadJobs = async (page = 1, search = '', locationFilter = '', tagFilter = '') => {
    setLoading(true)
    try {
      const data = await getJobs(page, jobsPerPage, search, locationFilter, tagFilter)
      setJobs(data.jobs)
      setTotalJobs(data.total)
    } catch (error) {
      console.error('Error loading jobs:', error)
    } finally {
      setLoading(false)
    }
  }

  const loadTags = async () => {
    try {
      const data = await getTags()
      setTags(data)
    } catch (error) {
      console.error('Error loading tags:', error)
    }
  }

  const handleScrape = async () => {
    if (!searchQuery) {
      alert('Please enter a search query')
      return
    }
    setLoading(true)
    try {
      await scrapeJobs(searchQuery, location)
      await loadJobs(1)
      setCurrentPage(1)
      await loadTags()
    } catch (error) {
      console.error('Error scraping jobs:', error)
      alert('Error scraping jobs. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const toggleTag = (tagName) => {
    setSelectedTags(prev =>
      prev.includes(tagName)
        ? prev.filter(t => t !== tagName)
        : [...prev, tagName]
    )
    // Reset to page 1 when tag changes
    setCurrentPage(1)
  }

  // Debounced search handler
  const handleSearchChange = (value) => {
    setSearchQuery(value)
    setCurrentPage(1)
    setShowSavedJobs(false)
  }

  const handleLocationChange = (value) => {
    setLocation(value)
    setCurrentPage(1)
    setShowSavedJobs(false)
  }

  // Get saved jobs
  const getSavedJobs = () => {
    const bookmarkedIds = getBookmarks()
    return jobs.filter(job => bookmarkedIds.includes(job.id))
  }

  // Display jobs (either all or saved)
  const displayJobs = showSavedJobs ? getSavedJobs() : jobs
  const displayTotal = showSavedJobs ? getSavedJobs().length : totalJobs

  const totalPages = Math.ceil(totalJobs / jobsPerPage)

  const paginate = (pageNumber) => {
    if (pageNumber >= 1 && pageNumber <= totalPages) {
      setCurrentPage(pageNumber)
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900">
      {/* Header */}
      <header className="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-3 sm:px-4 lg:px-8">
          <div className="flex items-center justify-between h-14 sm:h-16">
            <div className="flex items-center space-x-2 sm:space-x-3">
              <Briefcase className="h-6 w-6 sm:h-8 sm:w-8 text-primary" />
              <h1 className="text-lg sm:text-xl font-bold text-slate-900 dark:text-white">Care Jobs</h1>
            </div>
            <div className="flex items-center space-x-2 sm:space-x-4">
              {isAuthenticated() && (
                <button
                  onClick={() => setShowSavedJobs(!showSavedJobs)}
                  className={`flex items-center space-x-1 sm:space-x-2 px-2 sm:px-4 py-2 rounded-lg transition-colors ${
                    showSavedJobs
                      ? 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300'
                      : 'text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800'
                  }`}
                >
                  <Heart className={`h-4 w-4 ${showSavedJobs ? 'fill-current' : ''}`} />
                  <span className="hidden sm:inline text-sm">Saved</span>
                </button>
              )}
              <button
                onClick={() => setShowRecommendations(!showRecommendations)}
                className={`flex items-center space-x-1 sm:space-x-2 px-2 sm:px-4 py-2 rounded-lg transition-colors ${
                  showRecommendations
                    ? 'bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300'
                    : 'text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800'
                }`}
              >
                <Sparkles className="h-4 w-4" />
                <span className="hidden sm:inline text-sm">AI</span>
              </button>
              {isAuthenticated() ? (
                <>
                  <div className="relative profile-menu-container">
                    <button
                      onClick={() => setShowProfileMenu(!showProfileMenu)}
                      className="flex items-center space-x-1 sm:space-x-2 text-slate-600 hover:text-primary transition-colors"
                    >
                      <User className="h-4 w-4 sm:h-5 sm:w-5" />
                      <span className="hidden sm:inline text-sm">Profile</span>
                    </button>
                    {showProfileMenu && (
                      <div className="absolute right-0 top-full mt-2 w-56 bg-white dark:bg-slate-800 rounded-lg shadow-lg border border-slate-200 dark:border-slate-700 py-2 z-50">
                        <div className="px-4 py-2 border-b border-slate-100 dark:border-slate-700">
                          <p className="text-sm font-medium text-slate-900 dark:text-white">{getUserInfo()?.username || 'User'}</p>
                          <p className="text-xs text-slate-500 dark:text-slate-400">{getUserInfo()?.email || ''}</p>
                          <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">Role: {getUserInfo()?.role || 'user'}</p>
                        </div>
                        {isAdmin() && (
                          <Link
                            to="/admin"
                            onClick={() => setShowProfileMenu(false)}
                            className="flex items-center space-x-2 px-4 py-2 text-slate-600 dark:text-slate-300 hover:text-primary hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
                          >
                            <Shield className="h-4 w-4" />
                            <span className="text-sm">Admin Dashboard</span>
                          </Link>
                        )}
                        <button
                          onClick={handleLogout}
                          className="w-full flex items-center space-x-2 px-4 py-2 text-slate-600 dark:text-slate-300 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                        >
                          <LogOut className="h-4 w-4" />
                          <span className="text-sm">Logout</span>
                        </button>
                      </div>
                    )}
                  </div>
                </>
              ) : (
                <>
                  <Link
                    to="/login"
                    className="flex items-center space-x-1 sm:space-x-2 text-slate-600 hover:text-primary transition-colors"
                  >
                    <LogIn className="h-4 w-4 sm:h-5 sm:w-5" />
                    <span className="hidden sm:inline text-sm">Login</span>
                  </Link>
                  <Link
                    to="/signup"
                    className="flex items-center space-x-1 sm:space-x-2 px-2 sm:px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors text-sm"
                  >
                    <UserPlus className="h-4 w-4 sm:h-5 sm:w-5" />
                    <span className="hidden sm:inline">Sign Up</span>
                  </Link>
                </>
              )}
              {/* Dark Mode Toggle - Far Right */}
              <button
                onClick={toggleDark}
                className="ml-2 flex items-center justify-center w-10 h-10 rounded-full bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors"
                title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
              >
                {isDark ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* AI Recommendations Panel */}
      {showRecommendations && (
        <AIRecommendations
          jobs={jobs}
          onClose={() => setShowRecommendations(false)}
        />
      )}

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-3 sm:px-4 lg:px-8 py-4 sm:py-8">
        {/* Search Section */}
        <div className="mb-4 sm:mb-8">
          <SearchBar
            searchQuery={searchQuery}
            setSearchQuery={handleSearchChange}
            location={location}
            setLocation={handleLocationChange}
            onSearch={handleScrape}
            loading={loading}
          />
        </div>

        <div className="flex flex-col lg:flex-row gap-4 sm:gap-8">
          {/* Sidebar */}
          <div className="lg:w-64 lg:flex-shrink-0 order-2 lg:order-1">
            <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-4 sm:p-6">
              <div className="flex items-center space-x-2 mb-3 sm:mb-4">
                <Filter className="h-4 w-4 sm:h-5 sm:w-5 text-primary" />
                <h2 className="font-semibold text-slate-900 dark:text-white text-sm sm:text-base">Filters</h2>
              </div>
              <TagFilter
                tags={tags}
                selectedTags={selectedTags}
                onToggleTag={toggleTag}
              />
            </div>
          </div>

          {/* Job Listings */}
          <div className="flex-1 order-1 lg:order-2">
            <div className="flex items-center justify-between mb-4 sm:mb-6">
              <div className="flex items-center space-x-2">
                <Search className="h-4 w-4 sm:h-5 sm:w-5 text-slate-400 dark:text-slate-500" />
                <span className="text-slate-600 dark:text-slate-400 text-sm sm:text-base">
                  {showSavedJobs ? `${displayJobs.length} saved jobs` : `${displayTotal} jobs found`}
                </span>
              </div>
            </div>

            {loading ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
                <h3 className="text-lg font-medium text-slate-900 mb-2">
                  Loading jobs...
                </h3>
                <p className="text-slate-600">
                  Fetching from 6 job sources
                </p>
              </div>
            ) : jobs.length === 0 ? (
              <div className="text-center py-12">
                <Briefcase className="h-12 w-12 text-slate-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-slate-900 mb-2">
                  No jobs found
                </h3>
                <p className="text-slate-600">
                  Try adjusting your search or filters
                </p>
              </div>
            ) : (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {displayJobs.map((job) => (
                    <JobCard key={job.id} job={job} />
                  ))}
                </div>

                {/* Pagination */}
                {totalPages > 1 && (
                  <div className="flex justify-center items-center flex-wrap gap-1 sm:gap-2 mt-6 sm:mt-8">
                    {/* Previous Button */}
                    <button
                      onClick={() => paginate(currentPage - 1)}
                      disabled={currentPage === 1}
                      className="px-2 py-1 sm:px-3 sm:py-2 border border-slate-300 dark:border-slate-600 rounded-lg text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed text-xs sm:text-sm"
                    >
                      Previous
                    </button>

                    {/* Page Numbers */}
                    {(() => {
                      const pages = []
                      const maxVisible = 3

                      // Always show first page
                      pages.push(1)

                      // Calculate start and end of visible range around current page
                      let start = Math.max(2, currentPage - 1)
                      let end = Math.min(totalPages - 1, currentPage + 1)

                      // Adjust if at the beginning
                      if (currentPage <= 2) {
                        end = Math.min(totalPages - 1, maxVisible)
                      }
                      // Adjust if at the end
                      if (currentPage >= totalPages - 1) {
                        start = Math.max(2, totalPages - maxVisible + 1)
                      }

                      // Add ellipsis after first page if needed
                      if (start > 2) {
                        pages.push('...')
                      }

                      // Add visible pages
                      for (let i = start; i <= end; i++) {
                        if (i > 1 && i < totalPages) {
                          pages.push(i)
                        }
                      }

                      // Add ellipsis before last page if needed
                      if (end < totalPages - 1) {
                        pages.push('...')
                      }

                      // Always show last page if more than 1 page
                      if (totalPages > 1) {
                        pages.push(totalPages)
                      }

                      return pages.map((pageNum, index) => (
                        <button
                          key={index}
                          onClick={() => typeof pageNum === 'number' && paginate(pageNum)}
                          disabled={pageNum === '...'}
                          className={`px-2 py-1 sm:px-3 sm:py-2 rounded-lg text-xs sm:text-sm font-medium transition-colors ${
                            currentPage === pageNum
                              ? 'bg-primary text-white'
                              : pageNum === '...'
                              ? 'text-slate-400 dark:text-slate-500 cursor-default'
                              : 'border border-slate-300 dark:border-slate-600 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700'
                          }`}
                        >
                          {pageNum}
                        </button>
                      ))
                    })()}

                    {/* Next Button */}
                    <button
                      onClick={() => paginate(currentPage + 1)}
                      disabled={currentPage === totalPages}
                      className="px-2 py-1 sm:px-3 sm:py-2 border border-slate-300 dark:border-slate-600 rounded-lg text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed text-xs sm:text-sm"
                    >
                      Next
                    </button>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}

export default Dashboard
