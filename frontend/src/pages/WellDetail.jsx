import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts'
import api from '../services/api'

export default function WellDetail() {
  const { wellId } = useParams()
  const [well, setWell] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchWell = async () => {
      try {
        const response = await api.get(`/well/${wellId}`)
        setWell(response.data)
      } catch {
        setWell({
          well_id: wellId,
          current_depth: 14500,
          total_depth: 18000,
          current_risk: 0.62,
          risk_level: 'high_risk',
          formation_type: 'shale',
          drilling_phase: 'production',
          parameters: {
            wob: 28.5, rpm: 120, torque: 18500, rop: 45.2,
            mud_density: 11.8, ecd: 12.4, vibration_level: 5.8, hole_cleaning_index: 0.58
          },
          risk_history: Array.from({ length: 50 }, (_, i) => ({
            depth: 10000 + i * 90,
            risk: 0.3 + Math.random() * 0.4 + (i > 35 ? 0.2 : 0),
          })),
        })
      } finally {
        setLoading(false)
      }
    }
    fetchWell()
  }, [wellId])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="w-12 h-12 border-4 border-neon-blue/30 border-t-neon-blue rounded-full animate-spin" />
      </div>
    )
  }

  const riskColor = well.current_risk > 0.6 ? 'text-neon-red' : well.current_risk > 0.4 ? 'text-neon-orange' : 'text-neon-green'

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">{well.well_id}</h1>
          <p className="text-sm text-gray-400">{well.formation_type} | {well.drilling_phase} phase</p>
        </div>
        <div className={`text-3xl font-bold ${riskColor}`}>
          {(well.current_risk * 100).toFixed(0)}% Risk
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {Object.entries(well.parameters).map(([key, value]) => (
          <motion.div
            key={key}
            whileHover={{ scale: 1.02 }}
            className="glass-card p-4"
          >
            <p className="text-xs text-gray-400 uppercase">{key.replace(/_/g, ' ')}</p>
            <p className="text-xl font-bold mt-1">{typeof value === 'number' ? value.toFixed(1) : value}</p>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="glass-card p-6">
          <h3 className="text-sm font-medium text-gray-400 mb-4">Stuck Pipe Risk vs Depth</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={well.risk_history}>
              <defs>
                <linearGradient id="wellRiskGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ff3366" stopOpacity={0.4} />
                  <stop offset="95%" stopColor="#ff3366" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#243049" />
              <XAxis dataKey="depth" stroke="#6b7280" fontSize={11} tickFormatter={v => `${(v/1000).toFixed(0)}k`} />
              <YAxis stroke="#6b7280" fontSize={11} domain={[0, 1]} tickFormatter={v => `${(v*100).toFixed(0)}%`} />
              <Tooltip contentStyle={{ background: '#1a2035', border: '1px solid #243049', borderRadius: '8px' }} />
              <Area type="monotone" dataKey="risk" stroke="#ff3366" fill="url(#wellRiskGrad)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="glass-card p-6">
          <h3 className="text-sm font-medium text-gray-400 mb-4">Drilling Progress</h3>
          <div className="space-y-6 mt-8">
            <div>
              <div className="flex justify-between text-sm mb-2">
                <span className="text-gray-400">Current Depth</span>
                <span className="text-white font-medium">{well.current_depth?.toLocaleString()} ft</span>
              </div>
              <div className="w-full h-4 bg-dark-600 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${(well.current_depth / well.total_depth) * 100}%` }}
                  transition={{ duration: 1, ease: 'easeOut' }}
                  className="h-full bg-gradient-to-r from-neon-blue to-neon-purple rounded-full"
                />
              </div>
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>0 ft</span>
                <span>{well.total_depth?.toLocaleString()} ft (TD)</span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="p-3 bg-dark-600/50 rounded-lg">
                <p className="text-xs text-gray-400">Formation</p>
                <p className="text-sm font-medium capitalize mt-1">{well.formation_type}</p>
              </div>
              <div className="p-3 bg-dark-600/50 rounded-lg">
                <p className="text-xs text-gray-400">Phase</p>
                <p className="text-sm font-medium capitalize mt-1">{well.drilling_phase}</p>
              </div>
              <div className="p-3 bg-dark-600/50 rounded-lg">
                <p className="text-xs text-gray-400">Risk Level</p>
                <p className={`text-sm font-medium capitalize mt-1 ${riskColor}`}>{well.risk_level?.replace('_', ' ')}</p>
              </div>
              <div className="p-3 bg-dark-600/50 rounded-lg">
                <p className="text-xs text-gray-400">Completion</p>
                <p className="text-sm font-medium mt-1">{((well.current_depth / well.total_depth) * 100).toFixed(0)}%</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
