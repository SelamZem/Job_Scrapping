import { Building2, MapPin, ExternalLink, Tag as TagIcon } from 'lucide-react'

function JobCard({ job }) {
  return (
    <a
      href={job.url}
      target="_blank"
      rel="noopener noreferrer"
      className="block bg-white rounded-xl shadow-sm border border-slate-200 p-6 hover:shadow-md hover:border-primary transition-all cursor-pointer"
    >
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-slate-900 mb-1 hover:text-primary transition-colors">{job.title}</h3>
          <div className="flex items-center text-slate-600 text-sm">
            <Building2 className="h-4 w-4 mr-1" />
            {job.company}
          </div>
        </div>
        <span className="px-2 py-1 bg-secondary text-secondary-foreground text-xs rounded-full">
          {job.source}
        </span>
      </div>

      <div className="flex items-center text-slate-600 text-sm mb-4">
        <MapPin className="h-4 w-4 mr-1" />
        {job.location}
      </div>

      {job.salary && (
        <div className="text-sm text-slate-600 mb-4">
          <span className="font-medium">Salary:</span> {job.salary}
        </div>
      )}

      <p className="text-slate-600 text-sm mb-4 line-clamp-3">
        {job.description}
      </p>

      {job.tags && job.tags.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-4">
          {job.tags.slice(0, 5).map((tag, index) => (
            <span
              key={index}
              className="inline-flex items-center px-2 py-1 bg-accent text-accent-foreground text-xs rounded-md"
            >
              <TagIcon className="h-3 w-3 mr-1" />
              {tag}
            </span>
          ))}
          {job.tags.length > 5 && (
            <span className="text-xs text-slate-500">+{job.tags.length - 5} more</span>
          )}
        </div>
      )}

      <div className="flex items-center text-primary text-sm font-medium">
        View Job <ExternalLink className="h-4 w-4 ml-1" />
      </div>
    </a>
  )
}

export default JobCard
