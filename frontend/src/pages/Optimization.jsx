import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Settings, TrendingDown, Gauge, Droplets, RotateCcw } from 'lucide-react'
import api from '../services/api'

export default function Optimization() {
  const [recommendations, setRecommendations] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchRecs = async () => {
      try {
        const response = await api.get('/recommendation?well_id=WELL-002')
        setRecommendations(response.data)
      } catch {
        setRecommendations({
          well_id: 'WELL-002',
          risk_level: 'high_risk',
          recommendations: [
            { id: 'increase_circulation', title: 'Increase Circulation Rate', description: 'Improve annular velocity for better cuttings transport', expected_risk_reduction: 0.20, priority: 'high', category: 'hydraulics', implementation: 'Increase pump rate by 50-100 GPM. Verify ECD stays within safe window.' },
            { id: 'reduce_wob', title: 'Reduce Weight on Bit', description: 'Decrease WOB to reduce mechanical friction', expected_risk_reduction: 0.15, priority: 'high', category: 'mechanical', implementation: 'Gradually reduce WOB by 5-10 klbs while monitoring ROP.' },
            { id: 'optimize_mud', title: 'Optimize Mud Properties', description: 'Adjust mud weight and rheology for current formation', expected_risk_reduction: 0.22, priority: 'high', category: 'fluids', implementation: 'Reduce mud weight if overbalance exceeds 500 psi.' },
            { id: 'viscous_sweep', title: 'Pump Viscous Sweep', description: 'High-viscosity pill to improve cuttings removal', expected_risk_reduction: 0.16, priority: 'medium', category: 'fluids', implementation: 'Pump 30-50 bbl high-vis sweep (120-150 FV).' },
            { id: 'reduce_rpm', title: 'Reduce Rotary Speed', description: 'Lower RPM to mitigate stick-slip vibration', expected_risk_reduction: 0.12, priority: 'medium', category: 'mechanical', implementation: 'Reduce RPM by 20-40. Monitor vibration response.' },
          ],
          expected_risk_reduction: 0.34,
          priority: 'high',
        })
      } finally {
        setLoading(false)
      }
    }
    fetchRecs()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="w-12 h-12 border-4 border-neon-blue/30 border-t-neon-blue rounded-full animate-spin" />
      </div>
    )
  }

  const categoryIcons = {
    hydraulics: Droplets,
    mechanical: Settings,
    fluids: Gauge,
    operational: RotateCcw,
  }

  const priorityColors = {
    high: 'border-neon-red/30 bg-neon-red/5',
    medium: 'border-neon-orange/30 bg-neon-orange/5',
    low: 'border-neon-blue/30 bg-neon-blue/5',
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Drilling Optimization</h1>
          <p className="text-sm text-gray-400">AI recommendations for {recommendations?.well_id}</p>
        </div>
        <div className="flex items-center gap-2 px-4 py-2 glass-card border-neon-green/30">
          <TrendingDown className="w-5 h-5 text-neon-green" />
          <span className="text-sm font-medium text-neon-green">
            Potential {((recommendations?.expected_risk_reduction || 0) * 100).toFixed(0)}% risk reduction
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <motion.div whileHover={{ scale: 1.02 }} className="glass-card p-6 text-center">
          <p className="text-xs text-gray-400 uppercase">Current Risk</p>
          <p className="text-3xl font-bold text-neon-red mt-2">72%</p>
        </motion.div>
        <motion.div whileHover={{ scale: 1.02 }} className="glass-card p-6 text-center">
          <p className="text-xs text-gray-400 uppercase">After Optimization</p>
          <p className="text-3xl font-bold text-neon-green mt-2">
            {(72 - (recommendations?.expected_risk_reduction || 0) * 100).toFixed(0)}%
          </p>
        </motion.div>
        <motion.div whileHover={{ scale: 1.02 }} className="glass-card p-6 text-center">
          <p className="text-xs text-gray-400 uppercase">Actions Recommended</p>
          <p className="text-3xl font-bold text-neon-blue mt-2">{recommendations?.recommendations?.length}</p>
        </motion.div>
      </div>

      <div className="space-y-4">
        <h3 className="text-sm font-medium text-gray-400">Recommended Actions (Priority Order)</h3>
        {recommendations?.recommendations?.map((rec, idx) => {
          const IconComponent = categoryIcons[rec.category] || Settings
          return (
            <motion.div
              key={rec.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: idx * 0.08 }}
              className={`glass-card p-5 border ${priorityColors[rec.priority] || priorityColors.medium}`}
            >
              <div className="flex items-start gap-4">
                <div className="p-3 bg-dark-600/50 rounded-lg">
                  <IconComponent className="w-6 h-6 text-neon-blue" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-1">
                    <h4 className="text-base font-medium text-white">{rec.title}</h4>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      rec.priority === 'high' ? 'bg-neon-red/20 text-neon-red' : 'bg-neon-orange/20 text-neon-orange'
                    }`}>
                      {rec.priority}
                    </span>
                    <span className="text-xs px-2 py-0.5 rounded-full bg-dark-600 text-gray-300 capitalize">
                      {rec.category}
                    </span>
                  </div>
                  <p className="text-sm text-gray-400 mb-3">{rec.description}</p>
                  <div className="p-3 bg-dark-600/30 rounded-lg border border-dark-600/50">
                    <p className="text-xs text-gray-400 uppercase mb-1">Implementation</p>
                    <p className="text-sm text-gray-200">{rec.implementation}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-lg font-bold text-neon-green">-{(rec.expected_risk_reduction * 100).toFixed(0)}%</p>
                  <p className="text-xs text-gray-400">Risk reduction</p>
                </div>
              </div>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}
