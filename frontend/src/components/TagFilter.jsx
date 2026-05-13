import { X, ChevronDown, Check } from 'lucide-react'
import { useState, useEffect, useRef } from 'react'

function TagFilter({ tags, selectedTags, onApplyFilters, onClearFilters }) {
  const [isOpen, setIsOpen] = useState(false)
  const [tempSelected, setTempSelected] = useState([...selectedTags])
  const dropdownRef = useRef(null)

  const categories = [...new Set(tags.map(t => t.category))].filter(
    c => c !== 'role' && c !== 'industry'
  )

  const capitalize = (str) => str.charAt(0).toUpperCase() + str.slice(1)

  // Only sync tempSelected when dropdown is closed (don't interrupt active selection)
  useEffect(() => {
    if (!isOpen) {
      setTempSelected([...selectedTags])
    }
  }, [selectedTags])

  // Close on outside click — discard uncommitted changes
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setTempSelected([...selectedTags]) // discard
        setIsOpen(false)
      }
    }
    if (isOpen) document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [isOpen, selectedTags])

  const handleToggle = (tagName) => {
    setTempSelected(prev =>
      prev.includes(tagName) ? prev.filter(t => t !== tagName) : [...prev, tagName]
    )
  }

  const handleApply = () => {
    onApplyFilters(tempSelected)
    setIsOpen(false)
  }

  const handleClear = () => {
    setTempSelected([])
    onClearFilters()
    setIsOpen(false)
  }

  const removeOne = (tagName) => {
    const next = selectedTags.filter(t => t !== tagName)
    setTempSelected(next)
    onApplyFilters(next)
  }

  return (
    <div>
      {/* Active filter chips */}
      {selectedTags.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mb-3">
          {selectedTags.map(tag => (
            <span
              key={tag}
              className="inline-flex items-center gap-1 px-2 py-0.5 bg-primary/10 text-primary text-xs rounded-full font-medium"
            >
              {tag}
              <button onClick={() => removeOne(tag)} className="hover:opacity-70">
                <X className="h-3 w-3" />
              </button>
            </span>
          ))}
          <button
            onClick={handleClear}
            className="text-xs text-slate-400 hover:text-red-500 transition-colors ml-1"
          >
            Clear all
          </button>
        </div>
      )}

      {/* Dropdown */}
      <div className="relative" ref={dropdownRef}>
        {/* Trigger button */}
        <button
          onClick={() => setIsOpen(o => !o)}
          className="w-full flex items-center justify-between px-3 py-2.5 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-600 transition-colors text-sm"
        >
          <span className="text-slate-500 dark:text-slate-300 truncate">
            {tempSelected.length > 0
              ? `${tempSelected.length} skill${tempSelected.length > 1 ? 's' : ''} selected`
              : 'Select skills...'}
          </span>
          <ChevronDown className={`h-4 w-4 text-slate-400 flex-shrink-0 ml-2 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
        </button>

        {isOpen && (
          <div className="absolute z-50 w-full mt-1 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg shadow-xl">
            {/* Tag list */}
            <div className="max-h-60 overflow-y-auto p-2">
              {categories.length === 0 ? (
                <p className="text-slate-400 text-sm p-3 text-center">No tags yet</p>
              ) : (
                categories.map(category => (
                  <div key={category} className="mb-2">
                    <p className="text-xs font-semibold text-slate-400 dark:text-slate-500 uppercase tracking-wider px-2 py-1">
                      {capitalize(category)}
                    </p>
                    {tags
                      .filter(t => t.category === category)
                      .map(tag => (
                        <label
                          key={tag.id}
                          className="flex items-center gap-2 px-2 py-1.5 rounded hover:bg-slate-50 dark:hover:bg-slate-700 cursor-pointer select-none"
                        >
                          <input
                            type="checkbox"
                            checked={tempSelected.includes(tag.name)}
                            onChange={() => handleToggle(tag.name)}
                            className="w-4 h-4 rounded border-slate-300 accent-primary"
                          />
                          <span className="text-sm text-slate-700 dark:text-slate-300 flex-1">{tag.name}</span>
                          {tempSelected.includes(tag.name) && (
                            <Check className="h-3.5 w-3.5 text-primary flex-shrink-0" />
                          )}
                        </label>
                      ))}
                  </div>
                ))
              )}
            </div>

            {/* Footer buttons */}
            <div className="flex gap-2 p-2 border-t border-slate-100 dark:border-slate-700">
              <button
                onClick={handleClear}
                className="flex-1 px-3 py-2 text-xs font-medium text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-600 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors"
              >
                Clear
              </button>
              <button
                onClick={handleApply}
                className="flex-1 px-3 py-2 text-xs font-medium bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
              >
                Apply {tempSelected.length > 0 && `(${tempSelected.length})`}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default TagFilter
