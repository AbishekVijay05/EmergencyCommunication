'use client'

import { useState, useEffect } from 'react'

export default function IncidentsPage() {
  const [activeFilter, setActiveFilter] = useState('All')
  const [incidents, setIncidents] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    const fetchIncidents = async () => {
      try {
        const res = await fetch('http://localhost:8003/events/history')
        if (!res.ok) throw new Error('Failed to fetch data')
        const data = await res.json()
        setIncidents(data)
      } catch (err) {
        setError('Error connecting to Events microservice')
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    fetchIncidents()
    const interval = setInterval(fetchIncidents, 5000) // Poll every 5s
    return () => clearInterval(interval)
  }, [])

  const filteredIncidents = activeFilter === 'All' 
    ? incidents 
    : incidents.filter(inc => 
        (activeFilter === 'Critical' && inc.severity === 'critical') ||
        (activeFilter === 'Active' && inc.severity !== 'low') ||
        (activeFilter === 'Resolved' && inc.severity === 'low')
      )

  return (
    <div className="space-y-8 animate-fade-in">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold bg-gradient-to-r from-red-400 to-orange-500 bg-clip-text text-transparent">
            Live Incidents
          </h1>
          <p className="text-gray-400 mt-1">Real-time data streaming directly from Edge Nodes to Kafka</p>
        </div>
      </div>

      <div className="flex gap-4 border-b border-gray-800 pb-4">
        {['All', 'Active', 'Critical', 'Resolved'].map(f => (
          <button 
            key={f}
            onClick={() => setActiveFilter(f)}
            className={`px-4 py-1.5 rounded-full text-sm transition-all ${activeFilter === f ? 'bg-gray-800 text-white border border-gray-600' : 'text-gray-400 hover:text-white'}`}
          >
            {f}
          </button>
        ))}
      </div>

      {loading && <div className="text-center py-10 text-gray-500">Loading live Kafka stream...</div>}
      {error && <div className="text-center py-10 text-red-500">{error}</div>}

      <div className="space-y-4">
        {filteredIncidents.map((inc) => (
          <div key={inc.event_id} className="glass-card p-5 hover:border-gray-600/50 transition-all group flex items-center justify-between">
            <div className="flex items-center gap-6">
              <div className={`w-12 h-12 rounded-xl flex items-center justify-center bg-gray-800 border ${
                inc.severity === 'critical' ? 'border-red-500/50 text-red-500' :
                inc.severity === 'high' ? 'border-orange-500/50 text-orange-500' :
                inc.severity === 'medium' ? 'border-yellow-500/50 text-yellow-500' :
                'border-blue-500/50 text-blue-500'
              }`}>
                <span className="text-xl">
                  {inc.severity === 'critical' ? '🔥' : inc.severity === 'high' ? '⚡' : inc.severity === 'medium' ? '👀' : '🔧'}
                </span>
              </div>
              
              <div>
                <div className="flex items-center gap-3 mb-1">
                  <span className="font-mono text-xs text-command-400">{inc.event_id.split('-')[0]}</span>
                  <h3 className="text-lg font-semibold text-white group-hover:text-command-300 transition-colors uppercase">{inc.event_type.replace('_', ' ')}</h3>
                  <span className={`text-xs px-2 py-0.5 rounded-full ${
                    inc.severity === 'critical' ? 'bg-red-500/20 text-red-400' :
                    inc.severity === 'high' ? 'bg-orange-500/20 text-orange-400' :
                    inc.severity === 'medium' ? 'bg-yellow-500/20 text-yellow-400' :
                    'bg-blue-500/20 text-blue-400'
                  }`}>{inc.severity}</span>
                </div>
                <div className="flex items-center gap-4 text-sm text-gray-400">
                  <span className="flex items-center gap-1">📍 {inc.location} ({inc.zone})</span>
                  <span className="flex items-center gap-1">📊 Payload: {inc.payload.value} {inc.payload.unit}</span>
                  <span className="flex items-center gap-1">⏱️ {new Date(inc.created_at).toLocaleTimeString()}</span>
                </div>
              </div>
            </div>
          </div>
        ))}
        {!loading && filteredIncidents.length === 0 && (
          <div className="text-center py-10 text-gray-500">No matching incidents.</div>
        )}
      </div>
    </div>
  )
}
