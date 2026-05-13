import { Search, Loader2, MapPin } from 'lucide-react'

function SearchBar({ searchQuery, setSearchQuery, location, setLocation, onSearch, loading }) {
  const handleKeyDown = (e) => {
    if (e.key === 'Enter') onSearch?.()
  }

  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-4 sm:p-6">
      <div className="flex flex-col sm:flex-row gap-3">
        {/* Search input */}
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Job title, keywords..."
            className="w-full pl-9 pr-4 py-2.5 border border-slate-300 dark:border-slate-600 dark:bg-slate-700 dark:text-white dark:placeholder-slate-400 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none text-sm"
          />
        </div>

        {/* Location input */}
        <div className="relative flex-1 sm:max-w-[200px]">
          <MapPin className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <input
            type="text"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Location or Remote"
            className="w-full pl-9 pr-4 py-2.5 border border-slate-300 dark:border-slate-600 dark:bg-slate-700 dark:text-white dark:placeholder-slate-400 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none text-sm"
          />
        </div>

        {/* Search button */}
        <button
          onClick={onSearch}
          disabled={loading}
          className="flex items-center justify-center gap-2 px-5 py-2.5 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium whitespace-nowrap"
        >
          {loading ? (
            <><Loader2 className="h-4 w-4 animate-spin" /><span>Searching...</span></>
          ) : (
            <><Search className="h-4 w-4" /><span>Search</span></>
          )}
        </button>
      </div>
    </div>
  )
}

export default SearchBar
