import { Filter, X } from 'lucide-react'

function TagFilter({ tags, selectedTags, onToggleTag }) {
  const categories = [...new Set(tags.map(tag => tag.category))]

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-8">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Filter className="h-5 w-5 text-slate-600" />
          <h3 className="text-lg font-semibold text-slate-900">Filter by Tags</h3>
        </div>
        {selectedTags.length > 0 && (
          <div className="flex items-center space-x-2">
            <span className="text-sm text-slate-600">
              {selectedTags.length} selected
            </span>
            <button
              onClick={() => onToggleTag(null)}
              className="p-1 hover:bg-slate-100 rounded"
            >
              <X className="h-4 w-4 text-slate-500" />
            </button>
          </div>
        )}
      </div>

      {categories.length === 0 ? (
        <p className="text-slate-500 text-sm">No tags available. Scrape some jobs first!</p>
      ) : (
        <div className="space-y-4">
          {categories.map(category => (
            <div key={category}>
              <h4 className="text-sm font-medium text-slate-700 mb-2 capitalize">
                {category}
              </h4>
              <div className="flex flex-wrap gap-2">
                {tags
                  .filter(tag => tag.category === category)
                  .map(tag => (
                    <button
                      key={tag.id}
                      onClick={() => onToggleTag(tag.name)}
                      className={`px-3 py-1.5 text-sm rounded-lg transition-colors ${
                        selectedTags.includes(tag.name)
                          ? 'bg-primary text-primary-foreground'
                          : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
                      }`}
                    >
                      {tag.name}
                    </button>
                  ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default TagFilter
