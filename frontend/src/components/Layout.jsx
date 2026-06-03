import { Outlet, NavLink } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  LayoutDashboard, Activity, Brain, AlertTriangle, Settings, Gauge
} from 'lucide-react'

const navItems = [
  { path: '/', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/alerts', label: 'Alert Center', icon: AlertTriangle },
  { path: '/insights', label: 'AI Insights', icon: Brain },
  { path: '/optimization', label: 'Optimization', icon: Settings },
]

export default function Layout() {
  return (
    <div className="flex h-screen overflow-hidden">
      <aside className="w-64 bg-dark-800 border-r border-dark-600/50 flex flex-col">
        <div className="p-6 border-b border-dark-600/50">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-neon-blue to-neon-purple flex items-center justify-center">
              <Gauge className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-lg font-bold text-white">StuckPipe AI</h1>
              <p className="text-xs text-gray-400">Drilling Intelligence</p>
            </div>
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-1">
          {navItems.map(item => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.path === '/'}
              className={({ isActive }) =>
                isActive ? 'sidebar-link-active' : 'sidebar-link'
              }
            >
              <item.icon className="w-5 h-5" />
              <span className="text-sm font-medium">{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="p-4 border-t border-dark-600/50">
          <div className="glass-card p-3">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-neon-green animate-pulse" />
              <span className="text-xs text-gray-400">System Online</span>
            </div>
            <p className="text-xs text-gray-500 mt-1">Models: 3 active</p>
          </div>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="p-6"
        >
          <Outlet />
        </motion.div>
      </main>
    </div>
  )
}
