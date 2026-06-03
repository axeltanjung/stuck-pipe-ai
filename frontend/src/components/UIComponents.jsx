import { motion } from 'framer-motion';
import clsx from 'clsx';

export function KPICard({ title, value, subtitle, icon: Icon, trend, color = 'drilling' }) {
  const colorMap = {
    drilling: 'from-drilling-500/20 to-drilling-700/10 border-drilling-500/30',
    red: 'from-red-500/20 to-red-700/10 border-red-500/30',
    orange: 'from-orange-500/20 to-orange-700/10 border-orange-500/30',
    yellow: 'from-yellow-500/20 to-yellow-700/10 border-yellow-500/30',
    green: 'from-green-500/20 to-green-700/10 border-green-500/30',
    cyan: 'from-cyan-500/20 to-cyan-700/10 border-cyan-500/30',
  };

  return (
    <motion.div
      whileHover={{ scale: 1.02, y: -2 }}
      className={clsx(
        'glass-card p-5 bg-gradient-to-br border',
        colorMap[color]
      )}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs text-gray-400 uppercase tracking-wider mb-1">{title}</p>
          <p className="text-2xl font-bold text-white">{value}</p>
          {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
        </div>
        {Icon && (
          <div className="w-10 h-10 rounded-lg bg-dark-600/80 flex items-center justify-center">
            <Icon size={20} className="text-drilling-400" />
          </div>
        )}
      </div>
      {trend && (
        <div className={clsx('mt-3 text-xs font-medium', trend > 0 ? 'text-red-400' : 'text-green-400')}>
          {trend > 0 ? '↑' : '↓'} {Math.abs(trend)}% from last period
        </div>
      )}
    </motion.div>
  );
}

export function RiskBadge({ level }) {
  const badgeClass = {
    CRITICAL: 'risk-badge-critical',
    HIGH: 'risk-badge-high',
    WARNING: 'risk-badge-warning',
    LOW: 'risk-badge-low',
    NORMAL: 'risk-badge-normal',
  };

  return <span className={badgeClass[level] || 'risk-badge-normal'}>{level}</span>;
}

export function LoadingSpinner() {
  return (
    <div className="flex items-center justify-center py-12">
      <div className="w-8 h-8 border-2 border-drilling-500/30 border-t-drilling-500 rounded-full animate-spin" />
    </div>
  );
}

export function SectionHeader({ title, subtitle }) {
  return (
    <div className="mb-6">
      <h2 className="text-xl font-bold text-white">{title}</h2>
      {subtitle && <p className="text-sm text-gray-400 mt-1">{subtitle}</p>}
    </div>
  );
}
