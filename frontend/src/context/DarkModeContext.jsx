import { createContext, useContext, useState, useEffect } from 'react'

const DarkModeContext = createContext()

export function DarkModeProvider({ children }) {
  const [isDark, setIsDark] = useState(false)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    // Check localStorage first
    const stored = localStorage.getItem('care_jobs_dark_mode')
    if (stored !== null) {
      setIsDark(stored === 'true')
    } else {
      // Fallback to system preference
      setIsDark(window.matchMedia('(prefers-color-scheme: dark)').matches)
    }
    setMounted(true)
  }, [])

  useEffect(() => {
    if (!mounted) return
    
    // Apply dark class to document
    if (isDark) {
      document.documentElement.classList.add('dark')
      console.log('Dark mode enabled')
    } else {
      document.documentElement.classList.remove('dark')
      console.log('Light mode enabled')
    }
    // Save to localStorage
    localStorage.setItem('care_jobs_dark_mode', isDark.toString())
  }, [isDark, mounted])

  const toggleDark = () => {
    console.log('Toggling dark mode, current:', isDark)
    setIsDark(!isDark)
  }

  return (
    <DarkModeContext.Provider value={{ isDark, toggleDark }}>
      {children}
    </DarkModeContext.Provider>
  )
}

export const useDarkMode = () => useContext(DarkModeContext)
