import { useState } from 'react'
import { Sparkles, X, ExternalLink } from 'lucide-react'
import { getRecommendations } from '../services/api'

function AIRecommendations({ jobs, onClose }) {
  const [userProfile, setUserProfile] = useState({
    skills: '',
    roles: '',
    locations: ''
  })
  const [recommendations, setRecommendations] = useState([])
  const [loading, setLoading] = useState(false)

  const handleGetRecommendations = async () => {
    setLoading(true)
    try {
      const profile = {
        skills: userProfile.skills.split(',').map(s => s.trim()).filter(s => s),
        roles: userProfile.roles.split(',').map(s => s.trim()).filter(s => s),
        locations: userProfile.locations.split(',').map(s => s.trim()).filter(s => s)
      }
      
      const response = await getRecommendations(profile)
      setRecommendations(response.recommendations)
    } catch (error) {
      console.error('Error getting recommendations:', error)
      alert('Error getting recommendations. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-8">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2">
          <Sparkles className="h-5 w-5 text-primary" />
          <h3 className="text-lg font-semibold text-slate-900">AI-Powered Recommendations</h3>
        </div>
        <button
          onClick={onClose}
          className="p-1 hover:bg-slate-100 rounded"
        >
          <X className="h-4 w-4 text-slate-500" />
        </button>
      </div>

      <div className="grid gap-4 md:grid-cols-3 mb-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Your Skills (comma-separated)
          </label>
          <input
            type="text"
            value={userProfile.skills}
            onChange={(e) => setUserProfile({...userProfile, skills: e.target.value})}
            placeholder="e.g., Python, React, AWS"
            className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Preferred Roles
          </label>
          <input
            type="text"
            value={userProfile.roles}
            onChange={(e) => setUserProfile({...userProfile, roles: e.target.value})}
            placeholder="e.g., Developer, Engineer"
            className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700 mb-2">
            Preferred Locations
          </label>
          <input
            type="text"
            value={userProfile.locations}
            onChange={(e) => setUserProfile({...userProfile, locations: e.target.value})}
            placeholder="e.g., Remote, New York"
            className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-primary focus:border-transparent outline-none"
          />
        </div>
      </div>

      <button
        onClick={handleGetRecommendations}
        disabled={loading}
        className="w-full flex items-center justify-center space-x-2 px-6 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50 mb-6"
      >
        <Sparkles className="h-4 w-4" />
        <span>{loading ? 'Analyzing...' : 'Get Recommendations'}</span>
      </button>

      {recommendations.length > 0 && (
        <div>
          <h4 className="text-sm font-medium text-slate-700 mb-3">Recommended Jobs</h4>
          <div className="space-y-2">
            {recommendations.map((rec, index) => (
              <a
                key={index}
                href={rec.url || '#'}
                target="_blank"
                rel="noopener noreferrer"
                className="p-3 bg-accent rounded-lg flex items-center justify-between hover:bg-accent/80 transition-colors block"
              >
                <div>
                  <p className="font-medium text-slate-900">{rec.title}</p>
                  <p className="text-sm text-slate-600">{rec.company}</p>
                </div>
                <ExternalLink className="h-4 w-4 text-slate-500 flex-shrink-0" />
              </a>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default AIRecommendations
