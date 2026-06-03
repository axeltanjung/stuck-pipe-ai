import { motion } from 'framer-motion'

export default function KPICard({ title, value, subtitle, icon: Icon, color = 'blue', trend }) {
  const colorMap = {
    blue: 'from-neon-blue/20 to-neon-blue/5 border-neon-blue/30 text-neon-blue',
    green: 'from-neon-green/20 to-neon-green/5 border-neon-green/30 text-neon-green',
    orange: 'from-neon-orange/20 to-neon-orange/5 border-neon-orange/30 text-neon-orange',
    red: 'from-neon-red/20 to-neon-red/5 border-neon-red/30 text-neon-red',
    purple: 'from-neon-purple/20 to-neon-purple/5 border-neon-purple/30 text-neon-purple',
  }

  return (
    <motion.div
      whileHover={{ scale: 1.02, y: -2 }}
      className={`kpi-card bg-gradient-to-br ${colorMap[color]}`}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs text-gray-400 uppercase tracking-wider">{title}</p>
          <p className="text-3xl font-bold mt-2 text-white">{value}</p>
          {subtitle && <p className="text-sm text-gray-400 mt-1">{subtitle}</p>}
          {trend && (
            <p className={`text-xs mt-2 ${trend > 0 ? 'text-neon-red' : 'text-neon-green'}`}>
              {trend > 0 ? '↑' : '↓'} {Math.abs(trend)}% vs last period
            </p>
          )}
        </div>
        {Icon && (
          <div className={`p-3 rounded-lg bg-dark-700/50`}>
            <Icon className="w-6 h-6" />
          </div>
        )}
      </div>
    </motion.div>
  )
}
