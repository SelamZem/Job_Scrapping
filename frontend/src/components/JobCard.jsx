import { Building2, MapPin, ExternalLink, Tag as TagIcon, Heart } from 'lucide-react'
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { isBookmarked, toggleBookmark, canBookmark } from '../services/bookmarks'

function JobCard({ job }) {
  const [bookmarked, setBookmarked] = useState(false)
  const navigate = useNavigate()

  // Check bookmark status on mount
  useEffect(() => {
    setBookmarked(isBookmarked(job.id))
  }, [job.id])

  // Handle bookmark toggle
  const handleBookmark = (e) => {
    e.preventDefault()
    e.stopPropagation()
    
    // Check if user can bookmark (logged in)
    if (!canBookmark()) {
      alert('Please log in to save jobs')
      navigate('/login')
      return
    }
    
    const result = toggleBookmark(job.id)
    if (result.error) {
      alert(result.error)
      if (result.error.includes('log in')) {
        navigate('/login')
      }
      return
    }
    setBookmarked(result.isBookmarked)
  }

  // Strip HTML tags from text
  const stripHtml = (html) => {
    if (!html) return ''
    const tmp = document.createElement('div')
    tmp.innerHTML = html
    return tmp.textContent || tmp.innerText || ''
  }

  const cleanDescription = stripHtml(job.description)

  return (
    <a
      href={job.url}
      target="_blank"
      rel="noopener noreferrer"
      className="block bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-4 sm:p-6 hover:shadow-md hover:border-primary dark:hover:border-slate-600 transition-all cursor-pointer"
    >
      <div className="flex items-start justify-between mb-3 sm:mb-4">
        <div className="flex-1 min-w-0">
          <h3 className="text-base sm:text-lg font-semibold text-slate-900 dark:text-white mb-1 hover:text-primary dark:hover:text-primary transition-colors line-clamp-2">{job.title}</h3>
          <div className="flex items-center text-slate-600 dark:text-slate-400 text-xs sm:text-sm">
            <Building2 className="h-3 w-3 sm:h-4 sm:w-4 mr-1 flex-shrink-0" />
            <span className="truncate">{job.company}</span>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={handleBookmark}
            className={`p-1.5 rounded-full transition-colors ${
              bookmarked 
                ? 'text-red-500 hover:bg-red-50 dark:hover:bg-red-900/30' 
                : 'text-slate-400 dark:text-slate-500 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/30'
            }`}
            title={bookmarked ? 'Remove from saved jobs' : 'Save job'}
          >
            <Heart className={`h-4 w-4 sm:h-5 sm:w-5 ${bookmarked ? 'fill-current' : ''}`} />
          </button>
          <span className="px-2 py-1 bg-secondary dark:bg-slate-700 text-secondary-foreground dark:text-slate-300 text-xs rounded-full flex-shrink-0">
            {job.source}
          </span>
        </div>
      </div>

      <div className="flex items-center text-slate-600 dark:text-slate-400 text-xs sm:text-sm mb-3 sm:mb-4">
        <MapPin className="h-3 w-3 sm:h-4 sm:w-4 mr-1 flex-shrink-0" />
        <span className="truncate">{job.location}</span>
      </div>

      {job.salary && (
        <div className="text-xs sm:text-sm text-slate-600 dark:text-slate-400 mb-3 sm:mb-4">
          <span className="font-medium">Salary:</span> {job.salary}
        </div>
      )}

      <p className="text-slate-600 dark:text-slate-400 text-xs sm:text-sm mb-3 sm:mb-4 line-clamp-2 sm:line-clamp-3">
        {cleanDescription}
      </p>

      {job.tags && job.tags.length > 0 && (
        <div className="flex flex-wrap gap-1.5 sm:gap-2 mb-3 sm:mb-4">
          {job.tags.slice(0, 3).map((tag, index) => (
            <span
              key={index}
              className="inline-flex items-center px-1.5 sm:px-2 py-0.5 sm:py-1 bg-accent text-accent-foreground text-xs rounded-md"
            >
              <TagIcon className="h-2.5 w-2.5 sm:h-3 sm:w-3 mr-0.5 sm:mr-1" />
              <span className="truncate max-w-20 sm:max-w-none">{tag}</span>
            </span>
          ))}
          {job.tags.length > 3 && (
            <span className="text-xs text-slate-500 dark:text-slate-400">+{job.tags.length - 3} more</span>
          )}
        </div>
      )}

      <div className="flex items-center text-primary text-xs sm:text-sm font-medium">
        View Job <ExternalLink className="h-3 w-3 sm:h-4 sm:w-4 ml-1" />
      </div>
    </a>
  )
}

export default JobCard
