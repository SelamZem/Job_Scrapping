import { Building2, MapPin, ExternalLink, Tag as TagIcon } from 'lucide-react'

function JobCard({ job }) {
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
      className="block bg-white rounded-xl shadow-sm border border-slate-200 p-4 sm:p-6 hover:shadow-md hover:border-primary transition-all cursor-pointer"
    >
      <div className="flex items-start justify-between mb-3 sm:mb-4">
        <div className="flex-1 min-w-0">
          <h3 className="text-base sm:text-lg font-semibold text-slate-900 mb-1 hover:text-primary transition-colors line-clamp-2">{job.title}</h3>
          <div className="flex items-center text-slate-600 text-xs sm:text-sm">
            <Building2 className="h-3 w-3 sm:h-4 sm:w-4 mr-1 flex-shrink-0" />
            <span className="truncate">{job.company}</span>
          </div>
        </div>
        <span className="px-2 py-1 bg-secondary text-secondary-foreground text-xs rounded-full flex-shrink-0 ml-2">
          {job.source}
        </span>
      </div>

      <div className="flex items-center text-slate-600 text-xs sm:text-sm mb-3 sm:mb-4">
        <MapPin className="h-3 w-3 sm:h-4 sm:w-4 mr-1 flex-shrink-0" />
        <span className="truncate">{job.location}</span>
      </div>

      {job.salary && (
        <div className="text-xs sm:text-sm text-slate-600 mb-3 sm:mb-4">
          <span className="font-medium">Salary:</span> {job.salary}
        </div>
      )}

      <p className="text-slate-600 text-xs sm:text-sm mb-3 sm:mb-4 line-clamp-2 sm:line-clamp-3">
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
            <span className="text-xs text-slate-500">+{job.tags.length - 3} more</span>
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
