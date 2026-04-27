'use client'

import { useState, useEffect } from 'react'

interface Protocol {
  id: string
  name: string
  description: string
  version: number
  is_active: boolean
  created_at: string
}

interface ValidationResult {
  valid: boolean
  error?: string
  protocol_count?: number
  tree?: string
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8005'

export default function ProtocolsPage() {
  const [dslInput, setDslInput] = useState(
`WHEN fire_alert severity high
THEN
  notify fire_team
  lock building_zone_3
  dispatch ambulance
END`
  )
  const [protocols, setProtocols] = useState<Protocol[]>([])
  const [validation, setValidation] = useState<ValidationResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [deploying, setDeploying] = useState(false)
  const [deployStatus, setDeployStatus] = useState('')
  const [executeResult, setExecuteResult] = useState<any>(null)

  useEffect(() => {
    fetchProtocols()
  }, [])

  const fetchProtocols = async () => {
    try {
      const res = await fetch(`${API_BASE}/protocols`)
      if (res.ok) {
        const data = await res.json()
        setProtocols(data)
      }
    } catch (err) {
      console.error('Failed to fetch protocols:', err)
    }
  }

  const handleValidate = async () => {
    setLoading(true)
    setValidation(null)
    try {
      const res = await fetch(`${API_BASE}/protocols/validate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ dsl_source: dslInput }),
      })
      const data = await res.json()
      setValidation(data)
    } catch (err) {
      setValidation({ valid: false, error: 'Failed to connect to DSL Engine service' })
    } finally {
      setLoading(false)
    }
  }

  const handleDeploy = async () => {
    setDeploying(true)
    setDeployStatus('')
    try {
      const res = await fetch(`${API_BASE}/protocols/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          dsl_source: dslInput,
          name: `Protocol ${new Date().toISOString().slice(0, 16)}`,
          description: 'Deployed from dashboard editor',
        }),
      })
      if (res.ok) {
        const data = await res.json()
        setDeployStatus(`✅ Deployed! ID: ${data.id}`)
        fetchProtocols()
      } else {
        const err = await res.json()
        setDeployStatus(`❌ ${err.detail || 'Deploy failed'}`)
      }
    } catch (err) {
      setDeployStatus('❌ Failed to connect to DSL Engine service')
    } finally {
      setDeploying(false)
    }
  }

  const handleExecute = async (protocolId: string) => {
    try {
      const res = await fetch(`${API_BASE}/protocols/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ protocol_id: protocolId, trigger_event: {} }),
      })
      if (res.ok) {
        const data = await res.json()
        setExecuteResult(data)
      }
    } catch (err) {
      console.error('Execute failed:', err)
    }
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-500 bg-clip-text text-transparent">
          Emergency Protocols (DSL)
        </h1>
        <p className="text-gray-400 mt-1">Define and execute automated response logic</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-6">
          <div className="glass-card p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold text-white">Live Editor</h2>
              <span className="text-xs bg-purple-500/20 text-purple-400 px-2 py-1 rounded border border-purple-500/30">LALR Parser Active</span>
            </div>
            <textarea 
              value={dslInput}
              onChange={(e) => { setDslInput(e.target.value); setValidation(null); setDeployStatus('') }}
              className="w-full h-64 bg-gray-950 text-gray-300 font-mono text-sm p-4 rounded-lg border border-gray-800 focus:outline-none focus:border-purple-500/50 transition-colors resize-none"
              spellCheck="false"
            />

            {/* Validation feedback */}
            {validation && (
              <div className={`mt-3 p-3 rounded-lg text-sm ${validation.valid ? 'bg-green-500/10 border border-green-500/30 text-green-400' : 'bg-red-500/10 border border-red-500/30 text-red-400'}`}>
                {validation.valid ? (
                  <span>✅ Valid — {validation.protocol_count} protocol(s) parsed successfully</span>
                ) : (
                  <span>❌ {validation.error}</span>
                )}
              </div>
            )}

            {/* Deploy status */}
            {deployStatus && (
              <div className={`mt-3 p-3 rounded-lg text-sm ${deployStatus.startsWith('✅') ? 'bg-green-500/10 border border-green-500/30 text-green-400' : 'bg-red-500/10 border border-red-500/30 text-red-400'}`}>
                {deployStatus}
              </div>
            )}

            <div className="mt-4 flex justify-end gap-3">
              <button 
                onClick={handleValidate}
                disabled={loading}
                className="px-4 py-2 border border-gray-700 hover:bg-gray-800 text-gray-300 rounded-lg transition-colors text-sm disabled:opacity-50"
              >
                {loading ? 'Validating...' : 'Validate Syntax'}
              </button>
              <button 
                onClick={handleDeploy}
                disabled={deploying}
                className="px-4 py-2 bg-purple-600 hover:bg-purple-500 text-white rounded-lg transition-colors text-sm font-medium shadow-[0_0_15px_rgba(147,51,234,0.3)] disabled:opacity-50"
              >
                {deploying ? 'Deploying...' : 'Deploy Protocol'}
              </button>
            </div>
          </div>

          {/* Execute Result */}
          {executeResult && (
            <div className="glass-card p-6">
              <h2 className="text-lg font-semibold text-white mb-3">Execution Result</h2>
              <div className="bg-gray-950 rounded-lg p-4 font-mono text-xs text-gray-300 overflow-x-auto">
                <pre>{JSON.stringify(executeResult, null, 2)}</pre>
              </div>
            </div>
          )}
        </div>

        <div className="space-y-6">
          <div className="glass-card p-6 h-full">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold text-white">Active Protocols</h2>
              <button onClick={fetchProtocols} className="text-xs text-gray-500 hover:text-gray-300 transition-colors">↻ Refresh</button>
            </div>
            <div className="space-y-3">
              {protocols.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <p className="text-2xl mb-2">📜</p>
                  <p className="text-sm">No protocols deployed yet.</p>
                  <p className="text-xs mt-1">Write DSL in the editor and click Deploy.</p>
                </div>
              ) : (
                protocols.map(p => (
                  <div key={p.id} className="flex items-center justify-between p-4 bg-gray-900/50 border border-gray-800 rounded-lg hover:border-gray-700 transition-colors">
                    <div className="flex-1 min-w-0">
                      <h3 className="text-sm font-medium text-white truncate">{p.name}</h3>
                      <p className="text-xs text-gray-500 mt-1">
                        v{p.version} · {p.created_at ? new Date(p.created_at).toLocaleDateString() : 'N/A'}
                      </p>
                    </div>
                    <div className="flex items-center gap-2 ml-3">
                      <span className={`text-xs px-2 py-1 rounded-full ${p.is_active ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'}`}>
                        {p.is_active ? 'Active' : 'Inactive'}
                      </span>
                      <button 
                        onClick={() => handleExecute(p.id)}
                        className="text-xs px-2 py-1 bg-command-600/30 text-command-400 rounded hover:bg-command-600/50 transition-colors"
                      >
                        ▶ Run
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
