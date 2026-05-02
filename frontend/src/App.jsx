import { useState, useEffect } from 'react'
import { Search, Filter, Briefcase, MapPin, Building2, ExternalLink, Sparkles, Tag } from 'lucide-react'
import JobCard from './components/JobCard'
import SearchBar from './components/SearchBar'
import TagFilter from './components/TagFilter'
import AIRecommendations from './components/AIRecommendations'
import { getJobs, scrapeJobs, getTags } from './services/api'

function App() {
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

  useEffect(() => {
    loadJobs()
    loadTags()
  }, [])

  useEffect(() => {
    filterJobs()
    setCurrentPage(1)
  }, [jobs, selectedTags, searchQuery])

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
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <header className="bg-white border-b border-slate-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Briefcase className="h-8 w-8 text-primary" />
              <h1 className="text-2xl font-bold text-slate-900">Job Scrapping Platform</h1>
            </div>
            <button
              onClick={() => setShowRecommendations(!showRecommendations)}
              className="flex items-center space-x-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
            >
              <Sparkles className="h-4 w-4" />
              <span>AI Recommendations</span>
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <SearchBar
          searchQuery={searchQuery}
          setSearchQuery={setSearchQuery}
          location={location}
          setLocation={setLocation}
          onScrape={handleScrape}
          loading={loading}
        />

        {showRecommendations && (
          <AIRecommendations
            jobs={jobs}
            onClose={() => setShowRecommendations(false)}
          />
        )}

        <TagFilter
          tags={tags}
          selectedTags={selectedTags}
          onToggleTag={toggleTag}
        />

        <div className="mb-6 flex items-center justify-between">
          <h2 className="text-xl font-semibold text-slate-900">
            {filteredJobs.length} Jobs Found
          </h2>
          {selectedTags.length > 0 && (
            <button
              onClick={() => setSelectedTags([])}
              className="text-sm text-primary hover:underline"
            >
              Clear Filters
            </button>
          )}
        </div>

        {filteredJobs.length === 0 ? (
          <div className="text-center py-12">
            <Briefcase className="h-16 w-16 text-slate-300 mx-auto mb-4" />
            <p className="text-slate-500 text-lg">No jobs found</p>
            <p className="text-slate-400 text-sm mt-2">
              Try scraping jobs with a different search query
            </p>
          </div>
        ) : (
          <>
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {currentJobs.map(job => (
                <JobCard key={job.id} job={job} />
              ))}
            </div>

            {totalPages > 1 && (
              <div className="mt-8 flex items-center justify-center space-x-2">
                <button
                  onClick={() => paginate(currentPage - 1)}
                  disabled={currentPage === 1}
                  className="px-4 py-2 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Previous
                </button>
                
                {Array.from({ length: totalPages }, (_, i) => i + 1).map(page => (
                  <button
                    key={page}
                    onClick={() => paginate(page)}
                    className={`px-4 py-2 rounded-lg transition-colors ${
                      currentPage === page
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-white border border-slate-300 hover:bg-slate-50'
                    }`}
                  >
                    {page}
                  </button>
                ))}
                
                <button
                  onClick={() => paginate(currentPage + 1)}
                  disabled={currentPage === totalPages}
                  className="px-4 py-2 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  Next
                </button>
              </div>
            )}

            <div className="mt-4 text-center text-sm text-slate-500">
              Showing {indexOfFirstJob + 1} to {Math.min(indexOfLastJob, filteredJobs.length)} of {filteredJobs.length} jobs
            </div>
          </>
        )}
      </main>
    </div>
  )
}

export default App
