import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Emergency Command Center',
  description: 'Real-time emergency communication and incident management dashboard',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet" />
      </head>
      <body className="min-h-screen antialiased">
        <div className="flex h-screen overflow-hidden">
          {/* Sidebar */}
          <aside className="w-64 bg-gray-900/80 backdrop-blur-xl border-r border-gray-800 flex flex-col">
            <div className="p-6 border-b border-gray-800">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-command-500 to-command-700 flex items-center justify-center">
                  <span className="text-white font-bold text-lg">⚡</span>
                </div>
                <div>
                  <h1 className="text-lg font-bold text-white">ECCS</h1>
                  <p className="text-xs text-gray-500">Command Center</p>
                </div>
              </div>
            </div>

            <nav className="flex-1 p-4 space-y-1">
              <a href="/" className="nav-link nav-link-active">
                <span>📊</span> Dashboard
              </a>
              <a href="/incidents" className="nav-link">
                <span>🔥</span> Incidents
              </a>
              <a href="/messaging" className="nav-link">
                <span>💬</span> Messaging
              </a>
              <a href="/protocols" className="nav-link">
                <span>📜</span> Protocols
              </a>
              <a href="/analytics" className="nav-link">
                <span>🧠</span> Analytics
              </a>
              <a href="/project" className="nav-link">
                <span>📈</span> WBS / EVA
              </a>
            </nav>

            <div className="p-4 border-t border-gray-800">
              <div className="glass-card p-3">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                  <span className="text-xs text-gray-400">System Online</span>
                </div>
                <p className="text-xs text-gray-500 mt-1">Uptime: 99.9%</p>
              </div>
            </div>
          </aside>

          {/* Main content */}
          <main className="flex-1 overflow-y-auto">
            <div className="p-8">
              {children}
            </div>
          </main>
        </div>
      </body>
    </html>
  )
}
