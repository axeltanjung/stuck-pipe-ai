import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Activity, AlertTriangle, Gauge, Droplets, Thermometer } from 'lucide-react'
import KPICard from '../components/KPICard'
import { RiskAreaChart, RiskBarChart, RiskPieChart } from '../components/Charts'
import api from '../services/api'

const mockTrendData = Array.from({ length: 24 }, (_, i) => ({
  name: `${i}:00`,
  risk: Math.random() * 0.6 + 0.1,
  torque: Math.random() * 20000 + 5000,
  vibration: Math.random() * 8 + 1,
}))

export default function Dashboard() {
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const response = await api.get('/dashboard/summary')
        setSummary(response.data)
      } catch (err) {
        setSummary({
          total_wells: 8,
          active_wells: 8,
          high_risk_wells: 3,
          critical_alerts: 2,
          average_risk: 0.42,
          drilling_instability_index: 0.51,
          wells_summary: [
            { well_id: 'WELL-001', depth: 12500, risk: 0.72, risk_level: 'high_risk', formation: 'shale', region: 'Gulf of Mexico' },
            { well_id: 'WELL-002', depth: 9800, risk: 0.85, risk_level: 'critical', formation: 'sandstone', region: 'Permian Basin' },
            { well_id: 'WELL-003', depth: 15200, risk: 0.31, risk_level: 'low_risk', formation: 'limestone', region: 'North Sea' },
            { well_id: 'WELL-004', depth: 11000, risk: 0.55, risk_level: 'warning', formation: 'dolomite', region: 'Middle East' },
            { well_id: 'WELL-005', depth: 8500, risk: 0.18, risk_level: 'normal', formation: 'sandstone', region: 'West Africa' },
            { well_id: 'WELL-006', depth: 16800, risk: 0.63, risk_level: 'high_risk', formation: 'shale', region: 'Gulf of Mexico' },
            { well_id: 'WELL-007', depth: 7200, risk: 0.25, risk_level: 'low_risk', formation: 'limestone', region: 'Permian Basin' },
            { well_id: 'WELL-008', depth: 19500, risk: 0.78, risk_level: 'high_risk', formation: 'claystone', region: 'North Sea' },
          ],
          risk_distribution: { normal: 1, low_risk: 2, warning: 1, high_risk: 3, critical: 1 },
        })
      } finally {
        setLoading(false)
      }
    }
    fetchSummary()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="w-12 h-12 border-4 border-neon-blue/30 border-t-neon-blue rounded-full animate-spin" />
      </div>
    )
  }

  const riskDistData = summary ? [
    { name: 'Normal', value: summary.risk_distribution.normal },
    { name: 'Low', value: summary.risk_distribution.low_risk },
    { name: 'Warning', value: summary.risk_distribution.warning },
    { name: 'High', value: summary.risk_distribution.high_risk },
    { name: 'Critical', value: summary.risk_distribution.critical },
  ] : []

  const getRiskColor = (level) => {
    const map = { normal: 'text-neon-green', low_risk: 'text-neon-blue', warning: 'text-yellow-400', high_risk: 'text-neon-orange', critical: 'text-neon-red' }
    return map[level] || 'text-gray-400'
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Drilling Risk Intelligence</h1>
          <p className="text-sm text-gray-400">Real-time stuck pipe monitoring & prediction</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-neon-green animate-pulse" />
          <span className="text-xs text-gray-400">Live Monitoring</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard title="Active Wells" value={summary?.total_wells} subtitle="Across 5 regions" icon={Activity} color="blue" />
        <KPICard title="High Risk Wells" value={summary?.high_risk_wells} subtitle="Require attention" icon={AlertTriangle} color="red" trend={12} />
        <KPICard title="Avg Stuck Risk" value={`${(summary?.average_risk * 100).toFixed(0)}%`} subtitle="Fleet average" icon={Gauge} color="orange" trend={-5} />
        <KPICard title="Critical Alerts" value={summary?.critical_alerts} subtitle="Active now" icon={AlertTriangle} color="red" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-2">
          <RiskAreaChart data={mockTrendData} dataKey="risk" title="Stuck Pipe Risk Trend (24h)" />
        </div>
        <RiskPieChart data={riskDistData} title="Risk Distribution" />
      </div>

      <div className="glass-card p-6">
        <h3 className="text-sm font-medium text-gray-400 mb-4">Well Status Overview</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-dark-600">
                <th className="text-left py-3 px-4 text-gray-400 font-medium">Well ID</th>
                <th className="text-left py-3 px-4 text-gray-400 font-medium">Depth (ft)</th>
                <th className="text-left py-3 px-4 text-gray-400 font-medium">Formation</th>
                <th className="text-left py-3 px-4 text-gray-400 font-medium">Region</th>
                <th className="text-left py-3 px-4 text-gray-400 font-medium">Risk Level</th>
                <th className="text-left py-3 px-4 text-gray-400 font-medium">Risk %</th>
              </tr>
            </thead>
            <tbody>
              {summary?.wells_summary?.map((well, idx) => (
                <motion.tr
                  key={well.well_id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="border-b border-dark-600/50 hover:bg-dark-700/30"
                >
                  <td className="py-3 px-4">
                    <Link to={`/well/${well.well_id}`} className="text-neon-blue hover:underline font-medium">
                      {well.well_id}
                    </Link>
                  </td>
                  <td className="py-3 px-4 text-gray-300">{well.depth?.toLocaleString()}</td>
                  <td className="py-3 px-4 text-gray-300 capitalize">{well.formation}</td>
                  <td className="py-3 px-4 text-gray-300">{well.region}</td>
                  <td className="py-3 px-4">
                    <span className={`text-xs font-semibold uppercase ${getRiskColor(well.risk_level)}`}>
                      {well.risk_level?.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-2 bg-dark-600 rounded-full overflow-hidden">
                        <div
                          className={`h-full rounded-full ${well.risk > 0.6 ? 'bg-neon-red' : well.risk > 0.4 ? 'bg-neon-orange' : 'bg-neon-green'}`}
                          style={{ width: `${well.risk * 100}%` }}
                        />
                      </div>
                      <span className="text-gray-300">{(well.risk * 100).toFixed(0)}%</span>
                    </div>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
