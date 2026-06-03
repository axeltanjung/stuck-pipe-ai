import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar } from 'recharts'
import api from '../services/api'

export default function AIInsights() {
  const [explanation, setExplanation] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchInsights = async () => {
      try {
        const response = await api.get('/explain-risk?well_id=WELL-002')
        setExplanation(response.data)
      } catch {
        setExplanation({
          well_id: 'WELL-002',
          prediction: 0.78,
          risk_level: 'high_risk',
          top_risk_drivers: {
            differential_pressure: 0.32,
            torque_fluctuation: 0.24,
            cuttings_volume: 0.18,
            vibration_level: 0.14,
            hole_cleaning_index: 0.09,
          },
          top_protective_factors: {
            mud_flow_rate: -0.12,
            rop: -0.08,
            rpm: -0.05,
          },
          explanation_text: 'High differential pressure and torque fluctuation are primary risk drivers. Cuttings accumulation suggests inadequate hole cleaning.',
          confidence: 0.82,
        })
      } finally {
        setLoading(false)
      }
    }
    fetchInsights()
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="w-12 h-12 border-4 border-neon-blue/30 border-t-neon-blue rounded-full animate-spin" />
      </div>
    )
  }

  const featureData = explanation ? Object.entries(explanation.top_risk_drivers).map(([name, value]) => ({
    name: name.replace(/_/g, ' '),
    contribution: (value * 100).toFixed(1),
    fill: value > 0.2 ? '#ff3366' : value > 0.1 ? '#ff8800' : '#00d4ff',
  })) : []

  const radarData = explanation ? [
    ...Object.entries(explanation.top_risk_drivers).map(([name, value]) => ({
      factor: name.replace(/_/g, ' ').substring(0, 12),
      value: value * 100,
    })),
  ] : []

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">AI Explainability</h1>
        <p className="text-sm text-gray-400">SHAP-based prediction explanations for {explanation?.well_id}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <motion.div whileHover={{ scale: 1.02 }} className="glass-card p-6 text-center">
          <p className="text-xs text-gray-400 uppercase">Prediction</p>
          <p className="text-4xl font-bold text-neon-red mt-2">{(explanation?.prediction * 100).toFixed(0)}%</p>
          <p className="text-sm text-gray-400 mt-1">Stuck pipe probability</p>
        </motion.div>
        <motion.div whileHover={{ scale: 1.02 }} className="glass-card p-6 text-center">
          <p className="text-xs text-gray-400 uppercase">Confidence</p>
          <p className="text-4xl font-bold text-neon-blue mt-2">{(explanation?.confidence * 100).toFixed(0)}%</p>
          <p className="text-sm text-gray-400 mt-1">Model confidence</p>
        </motion.div>
        <motion.div whileHover={{ scale: 1.02 }} className="glass-card p-6 text-center">
          <p className="text-xs text-gray-400 uppercase">Risk Level</p>
          <p className="text-4xl font-bold text-neon-orange mt-2 capitalize">{explanation?.risk_level?.replace('_', ' ')}</p>
          <p className="text-sm text-gray-400 mt-1">Current assessment</p>
        </motion.div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="glass-card p-6">
          <h3 className="text-sm font-medium text-gray-400 mb-4">Feature Contribution (SHAP Values)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={featureData} layout="vertical" margin={{ left: 80 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#243049" />
              <XAxis type="number" stroke="#6b7280" fontSize={11} unit="%" />
              <YAxis type="category" dataKey="name" stroke="#6b7280" fontSize={11} width={100} />
              <Tooltip contentStyle={{ background: '#1a2035', border: '1px solid #243049', borderRadius: '8px' }} />
              <Bar dataKey="contribution" radius={[0, 4, 4, 0]}>
                {featureData.map((entry, idx) => (
                  <motion.rect key={idx} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="glass-card p-6">
          <h3 className="text-sm font-medium text-gray-400 mb-4">Risk Factor Radar</h3>
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={radarData}>
              <PolarGrid stroke="#243049" />
              <PolarAngleAxis dataKey="factor" stroke="#6b7280" fontSize={10} />
              <PolarRadiusAxis stroke="#6b7280" fontSize={10} />
              <Radar name="Risk" dataKey="value" stroke="#ff3366" fill="#ff3366" fillOpacity={0.3} strokeWidth={2} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="glass-card p-6">
        <h3 className="text-sm font-medium text-gray-400 mb-4">AI Explanation</h3>
        <div className="p-4 bg-dark-600/30 rounded-lg border border-neon-blue/20">
          <p className="text-gray-200 leading-relaxed">{explanation?.explanation_text}</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
          <div>
            <h4 className="text-sm font-medium text-neon-red mb-3">Risk Drivers</h4>
            <div className="space-y-2">
              {Object.entries(explanation?.top_risk_drivers || {}).map(([key, value]) => (
                <div key={key} className="flex items-center justify-between p-2 bg-neon-red/5 rounded border border-neon-red/10">
                  <span className="text-sm text-gray-300 capitalize">{key.replace(/_/g, ' ')}</span>
                  <span className="text-sm font-medium text-neon-red">+{(value * 100).toFixed(1)}%</span>
                </div>
              ))}
            </div>
          </div>
          <div>
            <h4 className="text-sm font-medium text-neon-green mb-3">Protective Factors</h4>
            <div className="space-y-2">
              {Object.entries(explanation?.top_protective_factors || {}).map(([key, value]) => (
                <div key={key} className="flex items-center justify-between p-2 bg-neon-green/5 rounded border border-neon-green/10">
                  <span className="text-sm text-gray-300 capitalize">{key.replace(/_/g, ' ')}</span>
                  <span className="text-sm font-medium text-neon-green">{(value * 100).toFixed(1)}%</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
