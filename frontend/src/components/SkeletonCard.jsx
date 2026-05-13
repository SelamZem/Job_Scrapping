function SkeletonCard() {
  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-4 sm:p-6 animate-pulse">
      {/* Header: title + bookmark button */}
      <div className="flex items-start justify-between mb-3 sm:mb-4">
        <div className="flex-1 min-w-0 pr-3">
          <div className="h-5 bg-slate-200 dark:bg-slate-700 rounded w-3/4 mb-2" />
          <div className="h-3 bg-slate-200 dark:bg-slate-700 rounded w-1/2" />
        </div>
        <div className="h-6 w-6 bg-slate-200 dark:bg-slate-700 rounded-full flex-shrink-0" />
      </div>

      {/* Location */}
      <div className="flex items-center gap-1 mb-3 sm:mb-4">
        <div className="h-3 w-3 bg-slate-200 dark:bg-slate-700 rounded-full flex-shrink-0" />
        <div className="h-3 bg-slate-200 dark:bg-slate-700 rounded w-2/5" />
      </div>

      {/* Salary */}
      <div className="h-3 bg-slate-200 dark:bg-slate-700 rounded w-1/3 mb-3 sm:mb-4" />

      {/* Description lines */}
      <div className="space-y-2 mb-3 sm:mb-4">
        <div className="h-3 bg-slate-200 dark:bg-slate-700 rounded w-full" />
        <div className="h-3 bg-slate-200 dark:bg-slate-700 rounded w-5/6" />
        <div className="h-3 bg-slate-200 dark:bg-slate-700 rounded w-4/6" />
      </div>

      {/* Tags */}
      <div className="flex gap-2 mb-3 sm:mb-4">
        <div className="h-5 bg-slate-200 dark:bg-slate-700 rounded-md w-16" />
        <div className="h-5 bg-slate-200 dark:bg-slate-700 rounded-md w-14" />
        <div className="h-5 bg-slate-200 dark:bg-slate-700 rounded-md w-20" />
      </div>

      {/* View Job link */}
      <div className="h-4 bg-slate-200 dark:bg-slate-700 rounded w-20" />
    </div>
  )
}

export default SkeletonCard
