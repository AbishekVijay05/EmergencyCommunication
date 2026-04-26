'use client'

export default function ProjectPage() {
  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold bg-gradient-to-r from-amber-400 to-orange-500 bg-clip-text text-transparent">
          WBS & Earned Value Analysis
        </h1>
        <p className="text-gray-400 mt-1">Project tracking and delivery metrics</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {[
          { label: 'Planned Value (PV)', value: '$125,000', color: 'text-gray-300' },
          { label: 'Earned Value (EV)', value: '$118,500', color: 'text-command-400' },
          { label: 'Schedule Performance (SPI)', value: '0.94', color: 'text-yellow-400', desc: 'Slightly behind schedule' },
          { label: 'Cost Performance (CPI)', value: '1.05', color: 'text-green-400', desc: 'Under budget' },
        ].map(m => (
          <div key={m.label} className="glass-card p-6 border-t-4 border-t-gray-800 hover:border-t-command-500 transition-colors">
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">{m.label}</h3>
            <div className={`text-2xl font-bold ${m.color}`}>{m.value}</div>
            {m.desc && <p className="text-xs text-gray-500 mt-2">{m.desc}</p>}
          </div>
        ))}
      </div>

      <div className="glass-card p-6">
        <h2 className="text-lg font-semibold text-white mb-4">Work Breakdown Structure (WBS)</h2>
        <div className="space-y-4">
          {[
            { id: '1.0', name: 'Emergency System Infrastructure', progress: 100, status: 'Complete' },
            { id: '1.1', name: 'Message Bus (Redpanda)', progress: 100, status: 'Complete' },
            { id: '1.2', name: 'Database & Cache (PostgreSQL/Redis)', progress: 100, status: 'Complete' },
            { id: '2.0', name: 'Core Microservices', progress: 100, status: 'Complete' },
            { id: '2.1', name: 'Auth & Gateway API', progress: 100, status: 'Complete' },
            { id: '2.2', name: 'DSL Protocol Engine', progress: 100, status: 'Complete' },
            { id: '3.0', name: 'Frontend Dashboard', progress: 85, status: 'In Progress' },
            { id: '4.0', name: 'System Testing', progress: 40, status: 'In Progress' },
          ].map(task => (
            <div key={task.id} className="flex items-center gap-4 group">
              <div className="w-12 text-xs font-mono text-gray-500">{task.id}</div>
              <div className={`flex-1 text-sm ${task.id.endsWith('.0') ? 'font-semibold text-white' : 'text-gray-400 pl-4'}`}>
                {task.name}
              </div>
              <div className="w-48 flex items-center gap-3">
                <div className="flex-1 h-2 bg-gray-800 rounded-full overflow-hidden">
                  <div 
                    className={`h-full rounded-full ${task.progress === 100 ? 'bg-green-500' : 'bg-command-500'}`} 
                    style={{ width: `${task.progress}%` }}
                  ></div>
                </div>
                <div className="w-12 text-xs text-right text-gray-500">{task.progress}%</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
