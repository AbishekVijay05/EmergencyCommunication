'use client'

export default function MessagingPage() {
  const channels = ['# global-alerts', '# alpha-team', '# beta-team', '# medical', '# command']
  
  const messages = [
    { sender: 'System', time: '10:42 AM', content: 'Routine system check completed. All nodes online.', isAlert: false },
    { sender: 'Alpha-Leader', time: '10:45 AM', content: 'Approaching Sector 4 for perimeter check.', isAlert: false },
    { sender: 'Gateway Proxy', time: '10:48 AM', content: 'CRITICAL: Smoke detected in Zone Alpha-3.', isAlert: true },
    { sender: 'Command', time: '10:49 AM', content: 'Alpha-Leader, please investigate Alpha-3 immediately.', isAlert: false },
    { sender: 'Alpha-Leader', time: '10:52 AM', content: 'Confirmed small electrical fire. Extinguishing now.', isAlert: false },
  ]

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col animate-fade-in">
      <div className="mb-6">
        <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-indigo-500 bg-clip-text text-transparent">
          Secure Messaging
        </h1>
        <p className="text-gray-400 mt-1">End-to-end AES-256-GCM encrypted comms</p>
      </div>

      <div className="flex-1 glass-card overflow-hidden flex">
        {/* Sidebar */}
        <div className="w-64 border-r border-gray-800 bg-gray-900/50 flex flex-col">
          <div className="p-4 border-b border-gray-800">
            <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Channels</h3>
          </div>
          <div className="p-2 space-y-1 overflow-y-auto flex-1">
            {channels.map((ch, i) => (
              <button 
                key={ch} 
                className={`w-full text-left px-4 py-2 rounded-lg text-sm transition-colors ${i === 0 ? 'bg-command-600/20 text-command-400 font-medium' : 'text-gray-400 hover:bg-gray-800 hover:text-white'}`}
              >
                {ch}
              </button>
            ))}
          </div>
        </div>

        {/* Chat Area */}
        <div className="flex-1 flex flex-col">
          <div className="p-4 border-b border-gray-800 bg-gray-900/30 flex items-center justify-between">
            <div>
              <h2 className="font-semibold text-white"># global-alerts</h2>
              <p className="text-xs text-gray-500">Encrypted Broadcast Channel</p>
            </div>
            <div className="flex items-center gap-2 text-xs text-green-400 bg-green-400/10 px-3 py-1 rounded-full border border-green-400/20">
              <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></span>
              Secure Connection
            </div>
          </div>

          <div className="flex-1 p-6 overflow-y-auto space-y-6">
            {messages.map((msg, i) => (
              <div key={i} className={`flex flex-col ${msg.sender === 'Command' ? 'items-end' : 'items-start'}`}>
                <div className="flex items-baseline gap-2 mb-1">
                  <span className={`text-sm font-medium ${msg.sender === 'System' ? 'text-gray-400' : msg.sender === 'Command' ? 'text-command-400' : 'text-indigo-400'}`}>
                    {msg.sender}
                  </span>
                  <span className="text-xs text-gray-600">{msg.time}</span>
                </div>
                <div className={`px-4 py-2 rounded-2xl max-w-[80%] text-sm ${
                  msg.isAlert 
                    ? 'bg-red-500/20 border border-red-500/30 text-red-100' 
                    : msg.sender === 'Command'
                      ? 'bg-command-600 text-white rounded-tr-none'
                      : 'bg-gray-800 text-gray-200 border border-gray-700 rounded-tl-none'
                }`}>
                  {msg.isAlert && <span className="mr-2">🚨</span>}
                  {msg.content}
                </div>
              </div>
            ))}
          </div>

          <div className="p-4 border-t border-gray-800 bg-gray-900/50">
            <div className="relative">
              <input 
                type="text" 
                placeholder="Type an encrypted message..." 
                className="w-full bg-gray-950 border border-gray-700 rounded-lg pl-4 pr-12 py-3 text-sm focus:outline-none focus:border-command-500 transition-colors"
              />
              <button className="absolute right-2 top-2 bottom-2 aspect-square bg-command-600 hover:bg-command-500 rounded text-white flex items-center justify-center transition-colors">
                ➤
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
