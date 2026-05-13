import { useState, useEffect } from 'react'
import { Search, Filter, Briefcase, Sparkles, User, LogOut, LogIn, UserPlus, Heart, Moon, Sun, Shield, X, SlidersHorizontal } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import JobCard from '../components/JobCard'
import SearchBar from '../components/SearchBar'
import TagFilter from '../components/TagFilter'
import AIRecommendations from '../components/AIRecommendations'
import SkeletonCard from '../components/SkeletonCard'
import { getJobs, scrapeJobs, getTags } from '../services/api'
import { isAuthenticated, logout, getUserInfo, isAdmin } from '../services/auth'
import { getBookmarks } from '../services/bookmarks'
import { useDarkMode } from '../context/DarkModeContext'

function useDebounce(value, delay) {
  const [debounced, setDebounced] = useState(value)
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delay)
    return () => clearTimeout(t)
  }, [value, delay])
  return debounced
}

function Dashboard() {
  const [jobs, setJobs] = useState([])
  const [totalJobs, setTotalJobs] = useState(0)
  const [tags, setTags] = useState([])
  const [selectedTags, setSelectedTags] = useState([])
  const [loading, setLoading] = useState(true)
  const [initialDone, setInitialDone] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [location, setLocation] = useState('')
  const [showRecommendations, setShowRecommendations] = useState(false)
  const [showSavedJobs, setShowSavedJobs] = useState(false)
  const [showProfileMenu, setShowProfileMenu] = useState(false)
  const [currentPage, setCurrentPage] = useState(1)
  const [bookmarkedIds, setBookmarkedIds] = useState([])
  const [showMobileFilter, setShowMobileFilter] = useState(false)
  const jobsPerPage = 12
  const navigate = useNavigate()
  const { isDark, toggleDark } = useDarkMode()

  const debouncedSearch = useDebounce(searchQuery, 400)
  const debouncedLocation = useDebounce(location, 400)

  // On mount: load 4 jobs fast, then full page, then tags/bookmarks
  useEffect(() => {
    const init = async () => {
      try {
        const quick = await getJobs(1, 4, '', '', [])
        setJobs(quick.jobs)
        setTotalJobs(quick.total)
        setLoading(false)
      } catch (e) {
        setLoading(false)
      }
      try {
        const full = await getJobs(1, jobsPerPage, '', '', [])
        setJobs(full.jobs)
        setTotalJobs(full.total)
      } catch (e) { /* silent */ }
      setInitialDone(true)
      loadTags()
      loadBookmarks()
    }
    init()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Search / location debounce
  useEffect(() => {
    if (!initialDone) return
    loadJobs(1, debouncedSearch, debouncedLocation, selectedTags)
    setCurrentPage(1)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debouncedSearch, debouncedLocation])

  // Page / tag change
  useEffect(() => {
    if (!initialDone) return
    loadJobs(currentPage, debouncedSearch, debouncedLocation, selectedTags)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentPage, JSON.stringify(selectedTags)])

  // Close profile menu on outside click
  useEffect(() => {
    const handler = (e) => {
      if (showProfileMenu && !e.target.closest('.profile-menu-container')) {
        setShowProfileMenu(false)
      }
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [showProfileMenu])

  const loadJobs = async (page = 1, search = '', loc = '', tagFilters = []) => {
    setLoading(true)
    try {
      const data = await getJobs(page, jobsPerPage, search, loc, tagFilters)
      setJobs(data.jobs)
      setTotalJobs(data.total)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const loadTags = async () => {
    try { setTags(await getTags()) } catch (e) { /* silent */ }
  }

  const loadBookmarks = async () => {
    try { setBookmarkedIds(await getBookmarks()) } catch (e) { /* silent */ }
  }

  const handleLogout = () => { logout(); navigate('/login') }

  const handleScrape = async () => {
    if (!searchQuery) return
    setLoading(true)
    try {
      await scrapeJobs(searchQuery, location)
      await loadJobs(1, searchQuery, location, selectedTags)
      setCurrentPage(1)
      loadTags()
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  const handleApplyFilters = (newTags) => { setSelectedTags([...newTags]); setCurrentPage(1) }
  const handleClearFilters = () => { setSelectedTags([]); setCurrentPage(1) }
  const handleSearchChange = (v) => { setSearchQuery(v); setShowSavedJobs(false) }
  const handleLocationChange = (v) => { setLocation(v); setShowSavedJobs(false) }

  const savedJobs = jobs.filter(j => bookmarkedIds.includes(j.id))
  const displayJobs = showSavedJobs ? savedJobs : jobs
  const displayTotal = showSavedJobs ? savedJobs.length : totalJobs
  const totalPages = Math.ceil(totalJobs / jobsPerPage)

  const paginate = (n) => {
    if (n >= 1 && n <= totalPages) {
      setCurrentPage(n)
      window.scrollTo({ top: 0, behavior: 'smooth' })
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
                  className={`flex items-center space-x-1 sm:space-x-2 px-2 sm:px-4 py-2 rounded-lg transition-colors ${showSavedJobs ? 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300' : 'text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800'}`}
                >
                  <Heart className={`h-4 w-4 ${showSavedJobs ? 'fill-current' : ''}`} />
                  <span className="hidden sm:inline text-sm">Saved</span>
                </button>
              )}
              <button
                onClick={() => setShowRecommendations(!showRecommendations)}
                className={`flex items-center space-x-1 sm:space-x-2 px-2 sm:px-4 py-2 rounded-lg transition-colors ${showRecommendations ? 'bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300' : 'text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800'}`}
              >
                <Sparkles className="h-4 w-4" />
                <span className="hidden sm:inline text-sm">AI</span>
              </button>
              {isAuthenticated() ? (
                <div className="relative profile-menu-container">
                  <button onClick={() => setShowProfileMenu(!showProfileMenu)} className="flex items-center space-x-1 sm:space-x-2 text-slate-600 hover:text-primary transition-colors">
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
                        <Link to="/admin" onClick={() => setShowProfileMenu(false)} className="flex items-center space-x-2 px-4 py-2 text-slate-600 dark:text-slate-300 hover:text-primary hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors">
                          <Shield className="h-4 w-4" />
                          <span className="text-sm">Admin Dashboard</span>
                        </Link>
                      )}
                      <button onClick={handleLogout} className="w-full flex items-center space-x-2 px-4 py-2 text-slate-600 dark:text-slate-300 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors">
                        <LogOut className="h-4 w-4" />
                        <span className="text-sm">Logout</span>
                      </button>
                    </div>
                  )}
                </div>
              ) : (
                <>
                  <Link to="/login" className="flex items-center space-x-1 sm:space-x-2 text-slate-600 hover:text-primary transition-colors">
                    <LogIn className="h-4 w-4 sm:h-5 sm:w-5" />
                    <span className="hidden sm:inline text-sm">Login</span>
                  </Link>
                  <Link to="/signup" className="flex items-center space-x-1 sm:space-x-2 px-2 sm:px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors text-sm">
                    <UserPlus className="h-4 w-4 sm:h-5 sm:w-5" />
                    <span className="hidden sm:inline">Sign Up</span>
                  </Link>
                </>
              )}
              <button onClick={toggleDark} className="ml-2 flex items-center justify-center w-10 h-10 rounded-full bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-600 transition-colors">
                {isDark ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* AI Recommendations */}
      {showRecommendations && <AIRecommendations jobs={jobs} onClose={() => setShowRecommendations(false)} />}

      {/* Mobile Filter Drawer */}
      {showMobileFilter && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" onClick={() => setShowMobileFilter(false)} />
          <div className="absolute bottom-0 left-0 right-0 bg-white dark:bg-slate-800 rounded-t-2xl shadow-2xl p-5 max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <SlidersHorizontal className="h-5 w-5 text-primary" />
                <h2 className="font-semibold text-slate-900 dark:text-white">Filters</h2>
              </div>
              <button onClick={() => setShowMobileFilter(false)} className="p-1.5 rounded-full hover:bg-slate-100 dark:hover:bg-slate-700 text-slate-500">
                <X className="h-5 w-5" />
              </button>
            </div>
            <TagFilter
              tags={tags}
              selectedTags={selectedTags}
              onApplyFilters={(t) => { handleApplyFilters(t); setShowMobileFilter(false) }}
              onClearFilters={() => { handleClearFilters(); setShowMobileFilter(false) }}
            />
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-3 sm:px-4 lg:px-8 py-4 sm:py-8">
        <div className="mb-4 sm:mb-6">
          <SearchBar
            searchQuery={searchQuery}
            setSearchQuery={handleSearchChange}
            location={location}
            setLocation={handleLocationChange}
            onSearch={handleScrape}
            loading={loading}
          />
        </div>

        {/* Mobile filter bar */}
        <div className="flex items-center justify-between mb-4 lg:hidden">
          <span className="text-slate-500 dark:text-slate-400 text-sm">
            {showSavedJobs ? `${displayJobs.length} saved` : `${displayTotal} jobs`}
          </span>
          <button
            onClick={() => setShowMobileFilter(true)}
            className={`flex items-center gap-2 px-3 py-2 rounded-lg border text-sm font-medium transition-colors ${selectedTags.length > 0 ? 'bg-primary text-white border-primary' : 'border-slate-300 dark:border-slate-600 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700'}`}
          >
            <SlidersHorizontal className="h-4 w-4" />
            Filters {selectedTags.length > 0 && `(${selectedTags.length})`}
          </button>
        </div>

        <div className="flex flex-col lg:flex-row gap-4 sm:gap-8">
          {/* Sidebar — desktop only */}
          <div className="hidden lg:block lg:w-64 lg:flex-shrink-0">
            <div className="lg:sticky lg:top-20">
              <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-4 sm:p-6">
                <div className="flex items-center space-x-2 mb-3 sm:mb-4">
                  <Filter className="h-4 w-4 sm:h-5 sm:w-5 text-primary" />
                  <h2 className="font-semibold text-slate-900 dark:text-white text-sm sm:text-base">Filters</h2>
                </div>
                <TagFilter tags={tags} selectedTags={selectedTags} onApplyFilters={handleApplyFilters} onClearFilters={handleClearFilters} />
              </div>
            </div>
          </div>

          {/* Job Listings */}
          <div className="flex-1">
            <div className="hidden lg:flex items-center mb-4 sm:mb-6">
              <Search className="h-4 w-4 sm:h-5 sm:w-5 text-slate-400 dark:text-slate-500 mr-2" />
              <span className="text-slate-600 dark:text-slate-400 text-sm sm:text-base">
                {showSavedJobs ? `${displayJobs.length} saved jobs` : `${displayTotal} jobs found`}
              </span>
            </div>

            {loading && jobs.length === 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {[...Array(12)].map((_, i) => <SkeletonCard key={i} />)}
              </div>
            ) : displayJobs.length === 0 && !loading ? (
              <div className="text-center py-12">
                <Briefcase className="h-12 w-12 text-slate-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-2">No jobs found</h3>
                <p className="text-slate-600 dark:text-slate-400">Try adjusting your search or filters</p>
              </div>
            ) : (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {displayJobs.map(job => <JobCard key={job.id} job={job} bookmarkedIds={bookmarkedIds} />)}
                  {loading && [...Array(3)].map((_, i) => <SkeletonCard key={`more-${i}`} />)}
                </div>

                {totalPages > 1 && (
                  <div className="flex justify-center items-center flex-wrap gap-1 sm:gap-2 mt-6 sm:mt-8">
                    <button onClick={() => paginate(currentPage - 1)} disabled={currentPage === 1} className="px-2 py-1 sm:px-3 sm:py-2 border border-slate-300 dark:border-slate-600 rounded-lg text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed text-xs sm:text-sm">
                      Previous
                    </button>
                    {(() => {
                      const pages = [1]
                      let start = Math.max(2, currentPage - 1)
                      let end = Math.min(totalPages - 1, currentPage + 1)
                      if (currentPage <= 2) end = Math.min(totalPages - 1, 3)
                      if (currentPage >= totalPages - 1) start = Math.max(2, totalPages - 2)
                      if (start > 2) pages.push('...')
                      for (let i = start; i <= end; i++) if (i > 1 && i < totalPages) pages.push(i)
                      if (end < totalPages - 1) pages.push('...')
                      if (totalPages > 1) pages.push(totalPages)
                      return pages.map((p, i) => (
                        <button key={i} onClick={() => typeof p === 'number' && paginate(p)} disabled={p === '...'}
                          className={`px-2 py-1 sm:px-3 sm:py-2 rounded-lg text-xs sm:text-sm font-medium transition-colors ${currentPage === p ? 'bg-primary text-white' : p === '...' ? 'text-slate-400 cursor-default' : 'border border-slate-300 dark:border-slate-600 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700'}`}>
                          {p}
                        </button>
                      ))
                    })()}
                    <button onClick={() => paginate(currentPage + 1)} disabled={currentPage === totalPages} className="px-2 py-1 sm:px-3 sm:py-2 border border-slate-300 dark:border-slate-600 rounded-lg text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed text-xs sm:text-sm">
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
