import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { AlertTriangle, AlertCircle, Info, CheckCircle, XCircle } from 'lucide-react'
import api from '../services/api'

const severityConfig = {
  critical: { color: 'border-neon-red/50 bg-neon-red/5', icon: XCircle, iconColor: 'text-neon-red', badge: 'bg-neon-red/20 text-neon-red' },
  high: { color: 'border-neon-orange/50 bg-neon-orange/5', icon: AlertTriangle, iconColor: 'text-neon-orange', badge: 'bg-neon-orange/20 text-neon-orange' },
  medium: { color: 'border-yellow-500/50 bg-yellow-500/5', icon: AlertCircle, iconColor: 'text-yellow-400', badge: 'bg-yellow-500/20 text-yellow-400' },
  low: { color: 'border-neon-blue/50 bg-neon-blue/5', icon: Info, iconColor: 'text-neon-blue', badge: 'bg-neon-blue/20 text-neon-blue' },
  info: { color: 'border-gray-500/50 bg-gray-500/5', icon: Info, iconColor: 'text-gray-400', badge: 'bg-gray-500/20 text-gray-400' },
}

export default function AlertCenter() {
  const [alerts, setAlerts] = useState([])
  const [filter, setFilter] = useState('all')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const response = await api.get('/alerts')
        setAlerts(response.data)
      } catch {
        setAlerts([
          { alert_id: 'a1', well_id: 'WELL-002', severity: 'critical', alert_type: 'stuck_pipe_critical', message: 'CRITICAL: Stuck pipe probability at 85%. Immediate action required.', risk_probability: 0.85, triggered_at: new Date().toISOString(), recommendations: ['Immediately increase circulation', 'Reduce WOB', 'Begin pipe rotation'] },
          { alert_id: 'a2', well_id: 'WELL-006', severity: 'high', alert_type: 'torque_anomaly', message: 'Torque fluctuation detected: 2.3x above baseline. Current torque: 24,500 ft-lbs.', risk_probability: 0.72, triggered_at: new Date().toISOString(), recommendations: ['Reduce RPM', 'Monitor for progressive increase', 'Consider backreaming'] },
          { alert_id: 'a3', well_id: 'WELL-008', severity: 'high', alert_type: 'poor_hole_cleaning', message: 'Poor hole cleaning detected. HCI: 0.35, Cuttings: 22%.', risk_probability: 0.68, triggered_at: new Date().toISOString(), recommendations: ['Increase flow rate', 'Pump viscous sweep', 'Increase pipe rotation'] },
          { alert_id: 'a4', well_id: 'WELL-001', severity: 'medium', alert_type: 'elevated_vibration', message: 'Elevated vibration: 7.8g. Monitor closely.', risk_probability: 0.48, triggered_at: new Date().toISOString(), recommendations: ['Adjust WOB/RPM', 'Monitor stick-slip index'] },
          { alert_id: 'a5', well_id: 'WELL-004', severity: 'medium', alert_type: 'pressure_instability', message: 'Standpipe pressure instability. Spike score: 0.62.', risk_probability: 0.55, triggered_at: new Date().toISOString(), recommendations: ['Check for pack-off', 'Verify pump efficiency'] },
        ])
      } finally {
        setLoading(false)
      }
    }
    fetchAlerts()
  }, [])

  const filteredAlerts = filter === 'all' ? alerts : alerts.filter(a => a.severity === filter)

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="w-12 h-12 border-4 border-neon-blue/30 border-t-neon-blue rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Alert Center</h1>
          <p className="text-sm text-gray-400">{alerts.length} active alerts across all wells</p>
        </div>
        <div className="flex gap-2">
          {['all', 'critical', 'high', 'medium', 'low'].map(level => (
            <button
              key={level}
              onClick={() => setFilter(level)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                filter === level ? 'bg-neon-blue/20 text-neon-blue border border-neon-blue/30' : 'text-gray-400 hover:text-white hover:bg-dark-600'
              }`}
            >
              {level.charAt(0).toUpperCase() + level.slice(1)}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <div className="glass-card p-4 text-center border-neon-red/30">
          <p className="text-2xl font-bold text-neon-red">{alerts.filter(a => a.severity === 'critical').length}</p>
          <p className="text-xs text-gray-400 mt-1">Critical</p>
        </div>
        <div className="glass-card p-4 text-center border-neon-orange/30">
          <p className="text-2xl font-bold text-neon-orange">{alerts.filter(a => a.severity === 'high').length}</p>
          <p className="text-xs text-gray-400 mt-1">High</p>
        </div>
        <div className="glass-card p-4 text-center border-yellow-500/30">
          <p className="text-2xl font-bold text-yellow-400">{alerts.filter(a => a.severity === 'medium').length}</p>
          <p className="text-xs text-gray-400 mt-1">Medium</p>
        </div>
        <div className="glass-card p-4 text-center border-neon-blue/30">
          <p className="text-2xl font-bold text-neon-blue">{alerts.filter(a => a.severity === 'low').length}</p>
          <p className="text-xs text-gray-400 mt-1">Low</p>
        </div>
      </div>

      <div className="space-y-4">
        {filteredAlerts.map((alert, idx) => {
          const config = severityConfig[alert.severity] || severityConfig.info
          const Icon = config.icon
          return (
            <motion.div
              key={alert.alert_id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.05 }}
              className={`glass-card p-5 border ${config.color}`}
            >
              <div className="flex items-start gap-4">
                <div className={`mt-1 ${config.iconColor}`}>
                  <Icon className="w-6 h-6" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${config.badge}`}>
                      {alert.severity.toUpperCase()}
                    </span>
                    <span className="text-xs text-gray-400">{alert.well_id}</span>
                    <span className="text-xs text-gray-500">{new Date(alert.triggered_at).toLocaleString()}</span>
                  </div>
                  <p className="text-sm text-gray-200 font-medium">{alert.message}</p>
                  <div className="mt-3">
                    <p className="text-xs text-gray-400 mb-2">Recommended Actions:</p>
                    <ul className="space-y-1">
                      {alert.recommendations?.map((rec, i) => (
                        <li key={i} className="text-xs text-gray-300 flex items-center gap-2">
                          <CheckCircle className="w-3 h-3 text-neon-green flex-shrink-0" />
                          {rec}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-lg font-bold text-white">{(alert.risk_probability * 100).toFixed(0)}%</p>
                  <p className="text-xs text-gray-400">Risk</p>
                </div>
              </div>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}
