import { useEffect, useState } from 'react'
import { CheckCircle, AlertCircle, X } from 'lucide-react'

function Toast({ message, type = 'success', onClose }) {
  const [visible, setVisible] = useState(true)

  useEffect(() => {
    const t = setTimeout(() => {
      setVisible(false)
      setTimeout(onClose, 300) // wait for fade-out
    }, 4000)
    return () => clearTimeout(t)
  }, [onClose])

  const isSuccess = type === 'success'

  return (
    <div
      className={`fixed bottom-6 left-1/2 -translate-x-1/2 z-50 flex items-center gap-3 px-5 py-3 rounded-xl shadow-xl border transition-all duration-300 ${
        visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
      } ${
        isSuccess
          ? 'bg-white dark:bg-slate-800 border-green-200 dark:border-green-800'
          : 'bg-white dark:bg-slate-800 border-red-200 dark:border-red-800'
      }`}
    >
      {isSuccess
        ? <CheckCircle className="h-5 w-5 text-green-500 flex-shrink-0" />
        : <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0" />
      }
      <span className="text-sm font-medium text-slate-700 dark:text-slate-200">{message}</span>
      <button onClick={() => { setVisible(false); setTimeout(onClose, 300) }} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300 ml-1">
        <X className="h-4 w-4" />
      </button>
    </div>
  )
}

export default Toast
