import { Filter, X, ChevronDown, Check } from 'lucide-react'
import { useState } from 'react'

function TagFilter({ tags, selectedTags, onToggleTag }) {
  const categories = [...new Set(tags.map(tag => tag.category))].filter(category => category !== 'role' && category !== 'industry')
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-4 sm:p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Filter className="h-4 w-4 sm:h-5 sm:w-5 text-slate-600 dark:text-slate-400" />
          <h3 className="text-base sm:text-lg font-semibold text-slate-900 dark:text-white">Filter by Skills</h3>
        </div>
        {selectedTags.length > 0 && (
          <div className="flex items-center space-x-2">
            <span className="text-xs sm:text-sm text-slate-600 dark:text-slate-400">
              {selectedTags.length} selected
            </span>
            <button
              onClick={() => onToggleTag(null)}
              className="p-1 hover:bg-slate-100 dark:hover:bg-slate-700 rounded"
            >
              <X className="h-3 w-3 sm:h-4 sm:w-4 text-slate-500" />
            </button>
          </div>
        )}
      </div>

      <div className="relative">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="w-full flex items-center justify-between px-4 py-3 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-600 transition-colors"
        >
          <span className="text-sm text-slate-600 dark:text-slate-300">
            {selectedTags.length > 0
              ? selectedTags.join(', ')
              : 'Select skills to filter...'}
          </span>
          <ChevronDown className={`h-4 w-4 text-slate-500 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
        </button>

        {isOpen && (
          <div className="absolute z-50 w-full mt-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg shadow-lg max-h-64 overflow-y-auto">
            {categories.length === 0 ? (
              <p className="text-slate-500 dark:text-slate-400 text-sm p-4">No tags available. Scrape some jobs first!</p>
            ) : (
              <div className="p-2">
                {categories.map(category => (
                  <div key={category} className="mb-3">
                    <h4 className="text-xs font-medium text-slate-500 dark:text-slate-400 mb-2 uppercase tracking-wide">
                      {category}
                    </h4>
                    <div className="space-y-1">
                      {tags
                        .filter(tag => tag.category === category)
                        .map(tag => (
                          <label
                            key={tag.id}
                            className="flex items-center space-x-3 px-3 py-2 hover:bg-slate-50 dark:hover:bg-slate-700 rounded cursor-pointer"
                          >
                            <input
                              type="checkbox"
                              checked={selectedTags.includes(tag.name)}
                              onChange={() => onToggleTag(tag.name)}
                              className="w-4 h-4 rounded border-slate-300 text-primary focus:ring-primary"
                            />
                            <span className="text-sm text-slate-700 dark:text-slate-300">{tag.name}</span>
                            {selectedTags.includes(tag.name) && (
                              <Check className="h-4 w-4 text-primary ml-auto" />
                            )}
                          </label>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default TagFilter
