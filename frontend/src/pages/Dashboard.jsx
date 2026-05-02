import { useState, useEffect } from 'react'
import { Search, Filter, Briefcase, Sparkles, User, LogOut } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import JobCard from '../components/JobCard'
import SearchBar from '../components/SearchBar'
import TagFilter from '../components/TagFilter'
import AIRecommendations from '../components/AIRecommendations'
import { getJobs, scrapeJobs, getTags } from '../services/api'
import { isAuthenticated, logout } from '../services/auth'

function Dashboard() {
  const [jobs, setJobs] = useState([])
  const [filteredJobs, setFilteredJobs] = useState([])
  const [tags, setTags] = useState([])
  const [selectedTags, setSelectedTags] = useState([])
  const [loading, setLoading] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [location, setLocation] = useState('')
  const [showRecommendations, setShowRecommendations] = useState(false)
  const [currentPage, setCurrentPage] = useState(1)
  const jobsPerPage = 9
  const navigate = useNavigate()

  useEffect(() => {
    if (!isAuthenticated()) {
      navigate('/login')
      return
    }
    loadJobs()
    loadTags()
  }, [navigate])

  useEffect(() => {
    filterJobs()
    setCurrentPage(1)
  }, [jobs, selectedTags, searchQuery])

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const loadJobs = async () => {
    try {
      const data = await getJobs()
      setJobs(data)
      setFilteredJobs(data)
    } catch (error) {
      console.error('Error loading jobs:', error)
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
      await loadJobs()
      await loadTags()
    } catch (error) {
      console.error('Error scraping jobs:', error)
      alert('Error scraping jobs. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const filterJobs = () => {
    let filtered = jobs

    if (selectedTags.length > 0) {
      filtered = filtered.filter(job =>
        job.tags.some(tag => selectedTags.includes(tag))
      )
    }

    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(job =>
        job.title.toLowerCase().includes(query) ||
        job.company.toLowerCase().includes(query) ||
        job.description.toLowerCase().includes(query)
      )
    }

    setFilteredJobs(filtered)
  }

  const toggleTag = (tagName) => {
    setSelectedTags(prev =>
      prev.includes(tagName)
        ? prev.filter(t => t !== tagName)
        : [...prev, tagName]
    )
  }

  const indexOfLastJob = currentPage * jobsPerPage
  const indexOfFirstJob = indexOfLastJob - jobsPerPage
  const currentJobs = filteredJobs.slice(indexOfFirstJob, indexOfLastJob)
  const totalPages = Math.ceil(filteredJobs.length / jobsPerPage)

  const paginate = (pageNumber) => setCurrentPage(pageNumber)

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <Briefcase className="h-8 w-8 text-primary" />
              <h1 className="text-xl font-bold text-slate-900">Job Scrapping Platform</h1>
            </div>
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setShowRecommendations(!showRecommendations)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                  showRecommendations
                    ? 'bg-purple-100 text-purple-700'
                    : 'text-slate-600 hover:bg-slate-100'
                }`}
              >
                <Sparkles className="h-4 w-4" />
                <span className="hidden sm:inline">AI Recommendations</span>
              </button>
              <div className="flex items-center space-x-2 text-slate-600">
                <User className="h-5 w-5" />
                <span className="hidden sm:inline">Profile</span>
              </div>
              <button
                onClick={handleLogout}
                className="flex items-center space-x-2 text-slate-600 hover:text-red-600 transition-colors"
              >
                <LogOut className="h-5 w-5" />
                <span className="hidden sm:inline">Logout</span>
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
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Section */}
        <div className="mb-8">
          <SearchBar
            searchQuery={searchQuery}
            setSearchQuery={setSearchQuery}
            location={location}
            setLocation={setLocation}
            onSearch={handleScrape}
            loading={loading}
          />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
              <div className="flex items-center space-x-2 mb-4">
                <Filter className="h-5 w-5 text-primary" />
                <h2 className="font-semibold text-slate-900">Filters</h2>
              </div>
              <TagFilter
                tags={tags}
                selectedTags={selectedTags}
                onToggleTag={toggleTag}
              />
            </div>
          </div>

          {/* Job Listings */}
          <div className="lg:col-span-3">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center space-x-2">
                <Search className="h-5 w-5 text-slate-400" />
                <span className="text-slate-600">
                  {filteredJobs.length} jobs found
                </span>
              </div>
            </div>

            {currentJobs.length === 0 ? (
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
                <div className="space-y-4">
                  {currentJobs.map((job) => (
                    <JobCard key={job.id} job={job} />
                  ))}
                </div>

                {/* Pagination */}
                {totalPages > 1 && (
                  <div className="flex justify-center items-center space-x-2 mt-8">
                    <button
                      onClick={() => paginate(currentPage - 1)}
                      disabled={currentPage === 1}
                      className="px-4 py-2 border border-slate-300 rounded-lg text-slate-600 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Previous
                    </button>
                    <span className="text-slate-600">
                      Page {currentPage} of {totalPages}
                    </span>
                    <button
                      onClick={() => paginate(currentPage + 1)}
                      disabled={currentPage === totalPages}
                      className="px-4 py-2 border border-slate-300 rounded-lg text-slate-600 hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
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
