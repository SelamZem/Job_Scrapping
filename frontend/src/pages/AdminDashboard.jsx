import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Activity, CheckCircle, XCircle, AlertTriangle, RefreshCw, Play, Server } from 'lucide-react'
import { isAuthenticated, getUserInfo, isAdmin, logout } from '../services/auth'
import api from '../services/api'

function AdminDashboard() {
  const [health, setHealth] = useState(null)
  const [testResults, setTestResults] = useState(null)
  const [loading, setLoading] = useState(true)
  const [testing, setTesting] = useState(false)
  const navigate = useNavigate()

  // Check if user is admin
  useEffect(() => {
    if (!isAuthenticated()) {
      navigate('/login')
      return
    }
    if (!isAdmin()) {
      alert('Admin access required')
      navigate('/')
      return
    }
    fetchHealth()
  }, [navigate])

  const fetchHealth = async () => {
    try {
      setLoading(true)
      const response = await api.get('/admin/health')
      setHealth(response.data)
    } catch (error) {
      if (error.response?.status === 401) {
        logout()
        navigate('/login')
        return
      }
      console.error('Failed to fetch health:', error)
    } finally {
      setLoading(false)
    }
  }

  const runTests = async () => {
    try {
      setTesting(true)
      const response = await api.post('/admin/scrapers/test')
      setTestResults(response.data)
    } catch (error) {
      if (error.response?.status === 401) {
        logout()
        navigate('/login')
        return
      }
      console.error('Failed to run tests:', error)
      alert('Failed to run tests: ' + (error.response?.data?.detail || error.message))
    } finally {
      setTesting(false)
    }
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="h-5 w-5 text-green-500" />
      case 'degraded':
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />
      case 'down':
        return <XCircle className="h-5 w-5 text-red-500" />
      default:
        return <Activity className="h-5 w-5 text-gray-400" />
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'healthy':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
      case 'degraded':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
      case 'down':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200'
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-slate-900 flex items-center justify-center">
        <div className="flex items-center space-x-2 text-slate-600 dark:text-slate-400">
          <RefreshCw className="h-5 w-5 animate-spin" />
          <span>Loading admin dashboard...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900">
      {/* Header */}
      <header className="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <Server className="h-6 w-6 text-primary" />
              <h1 className="text-xl font-bold text-slate-900 dark:text-white">Admin Dashboard</h1>
            </div>
            <div className="flex items-center space-x-3">
              <span className="text-sm text-slate-600 dark:text-slate-400">
                Logged in as: {getUserInfo()?.username}
              </span>
              <button
                onClick={() => navigate('/')}
                className="text-sm text-primary hover:underline"
              >
                Back to Jobs
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Overall Status */}
        <div className="mb-8">
          <div className={`rounded-xl p-6 ${getStatusColor(health?.overall_status)}`}>
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold">Overall System Status</h2>
                <p className="text-sm mt-1">
                  {health?.healthy || 0} of {health?.total_scrapers || 0} scrapers healthy
                </p>
              </div>
              <div className="flex items-center space-x-4">
                <div className="text-center">
                  <div className="text-2xl font-bold">{health?.healthy || 0}</div>
                  <div className="text-xs">Healthy</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold">{health?.degraded || 0}</div>
                  <div className="text-xs">Degraded</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold">{health?.down || 0}</div>
                  <div className="text-xs">Down</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex space-x-4 mb-8">
          <button
            onClick={fetchHealth}
            className="flex items-center space-x-2 px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
          >
            <RefreshCw className="h-4 w-4" />
            <span>Refresh Health</span>
          </button>
          <button
            onClick={runTests}
            disabled={testing}
            className="flex items-center space-x-2 px-4 py-2 bg-slate-600 text-white rounded-lg hover:bg-slate-700 transition-colors disabled:opacity-50"
          >
            <Play className="h-4 w-4" />
            <span>{testing ? 'Testing...' : 'Run Scraper Tests'}</span>
          </button>
        </div>

        {/* Test Results */}
        {testResults && (
          <div className="mb-8 bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 p-6">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white mb-4">
              Test Results ({testResults.successful}/{testResults.total} passed)
            </h3>
            <div className="space-y-2">
              {testResults.results.map((result, index) => (
                <div
                  key={index}
                  className={`flex items-center justify-between p-3 rounded-lg ${
                    result.status === 'success'
                      ? 'bg-green-50 dark:bg-green-900/30'
                      : 'bg-red-50 dark:bg-red-900/30'
                  }`}
                >
                  <div className="flex items-center space-x-3">
                    {result.status === 'success' ? (
                      <CheckCircle className="h-5 w-5 text-green-500" />
                    ) : (
                      <XCircle className="h-5 w-5 text-red-500" />
                    )}
                    <span className="font-medium text-slate-900 dark:text-white">{result.name}</span>
                  </div>
                  <div className="text-sm text-slate-600 dark:text-slate-400">
                    {result.status === 'success' ? (
                      <span>{result.jobs_found} jobs in {result.duration}s</span>
                    ) : (
                      <span className="text-red-600">{result.error}</span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Scraper Health Details */}
        <div className="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden">
          <div className="px-6 py-4 border-b border-slate-200 dark:border-slate-700">
            <h3 className="text-lg font-semibold text-slate-900 dark:text-white">Scraper Health Details</h3>
          </div>
          <div className="divide-y divide-slate-200 dark:divide-slate-700">
            {health?.scrapers?.length === 0 && (
              <div className="px-6 py-8 text-center text-slate-500 dark:text-slate-400">
                <Activity className="h-12 w-12 mx-auto mb-4 text-slate-300" />
                <p className="text-lg font-medium mb-2">No scraper data yet</p>
                <p className="text-sm mb-4">Scrapers need to run first to collect health data.</p>
                <button
                  onClick={runTests}
                  disabled={testing}
                  className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 disabled:opacity-50"
                >
                  {testing ? 'Testing...' : 'Run Scraper Tests Now'}
                </button>
              </div>
            )}
            {health?.scrapers?.map((scraper) => (
              <div key={scraper.name} className="px-6 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    {getStatusIcon(scraper.status)}
                    <div>
                      <div className="font-medium text-slate-900 dark:text-white">{scraper.name}</div>
                      <div className="text-sm text-slate-500 dark:text-slate-400">
                        Last run: {scraper.last_run ? new Date(scraper.last_run).toLocaleString() : 'Never'}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-6 text-sm">
                    <div className="text-center">
                      <div className="font-medium text-slate-900 dark:text-white">{scraper.success_rate}%</div>
                      <div className="text-slate-500 dark:text-slate-400">Success Rate</div>
                    </div>
                    <div className="text-center">
                      <div className="font-medium text-slate-900 dark:text-white">{scraper.total_runs}</div>
                      <div className="text-slate-500 dark:text-slate-400">Total Runs</div>
                    </div>
                    <div className="text-center">
                      <div className="font-medium text-slate-900 dark:text-white">{scraper.avg_jobs_per_run}</div>
                      <div className="text-slate-500 dark:text-slate-400">Avg Jobs</div>
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(scraper.status)}`}>
                      {scraper.status}
                    </span>
                  </div>
                </div>
                {scraper.last_error && (
                  <div className="mt-2 text-sm text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 p-2 rounded">
                    Last error: {scraper.last_error}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}

export default AdminDashboard
