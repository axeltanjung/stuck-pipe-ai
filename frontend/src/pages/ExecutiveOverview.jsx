import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import {
  BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, Tooltip, ResponsiveContainer, RadialBarChart, RadialBar
} from 'recharts';
import { Activity, AlertTriangle, TrendingUp, Radio, ShieldAlert, Gauge } from 'lucide-react';
import { KPICard, RiskBadge, LoadingSpinner, SectionHeader } from '../components/UIComponents';
import { getDashboardSummary } from '../api';

const RISK_COLORS = {
  critical: '#ef4444',
  high: '#f97316',
  warning: '#eab308',
  low: '#22c55e',
  normal: '#06b6d4',
};

export default function ExecutiveOverview() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadDashboard();
  }, []);

  async function loadDashboard() {
    try {
      const res = await getDashboardSummary();
      setData(res.data);
    } catch (err) {
      setData(generateMockData());
    } finally {
      setLoading(false);
    }
  }

  if (loading) return <LoadingSpinner />;
  if (!data) return <div className="text-gray-400">Failed to load data</div>;

  const riskDistData = Object.entries(data.risk_distribution).map(([key, value]) => ({
    name: key.charAt(0).toUpperCase() + key.slice(1),
    value,
    color: RISK_COLORS[key],
  }));

  const wellRiskData = Object.entries(data.well_risk_scores || {}).slice(0, 10).map(([well, risk]) => ({
    well: well.replace('WELL-', 'W'),
    risk: +(risk * 100).toFixed(1),
    fill: risk > 0.5 ? RISK_COLORS.high : risk > 0.3 ? RISK_COLORS.warning : RISK_COLORS.normal,
  }));

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Executive Overview</h1>
          <p className="text-sm text-gray-400 mt-1">Drilling Risk Intelligence Dashboard</p>
        </div>
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
          Live monitoring
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <KPICard
          title="Active Wells"
          value={data.total_wells}
          subtitle="Under monitoring"
          icon={Radio}
          color="cyan"
        />
        <KPICard
          title="High-Risk Wells"
          value={data.high_risk_wells}
          subtitle="Require attention"
          icon={ShieldAlert}
          color="red"
          trend={5}
        />
        <KPICard
          title="Active Alerts"
          value={data.active_alerts}
          subtitle="Across all wells"
          icon={AlertTriangle}
          color="orange"
        />
        <KPICard
          title="Avg Stuck Risk"
          value={`${(data.average_stuck_risk * 100).toFixed(1)}%`}
          subtitle="Fleet average"
          icon={Gauge}
          color="drilling"
          trend={-2}
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <motion.div className="glass-card p-5 lg:col-span-2" whileHover={{ scale: 1.005 }}>
          <SectionHeader title="Well Risk Ranking" subtitle="Top 10 wells by stuck pipe probability" />
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={wellRiskData}>
              <XAxis dataKey="well" tick={{ fill: '#9ca3af', fontSize: 11 }} />
              <YAxis tick={{ fill: '#9ca3af', fontSize: 11 }} domain={[0, 100]} />
              <Tooltip
                contentStyle={{ background: '#1a2332', border: '1px solid #2d3b50', borderRadius: 8 }}
                labelStyle={{ color: '#fff' }}
              />
              <Bar dataKey="risk" radius={[4, 4, 0, 0]}>
                {wellRiskData.map((entry, idx) => (
                  <Cell key={idx} fill={entry.fill} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </motion.div>

        <motion.div className="glass-card p-5" whileHover={{ scale: 1.005 }}>
          <SectionHeader title="Risk Distribution" subtitle="Event classification" />
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={riskDistData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={3}
                dataKey="value"
              >
                {riskDistData.map((entry, idx) => (
                  <Cell key={idx} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{ background: '#1a2332', border: '1px solid #2d3b50', borderRadius: 8 }}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="flex flex-wrap gap-2 mt-2 justify-center">
            {riskDistData.map((entry) => (
              <div key={entry.name} className="flex items-center gap-1 text-xs">
                <div className="w-2 h-2 rounded-full" style={{ background: entry.color }} />
                <span className="text-gray-400">{entry.name}</span>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      <motion.div className="glass-card p-5" whileHover={{ scale: 1.002 }}>
        <SectionHeader title="Well Status Matrix" subtitle="Click a well to view details" />
        <div className="grid grid-cols-4 md:grid-cols-5 lg:grid-cols-10 gap-2">
          {Object.entries(data.well_risk_scores || {}).map(([well, risk]) => (
            <button
              key={well}
              onClick={() => navigate(`/well/${well}`)}
              className="p-2 rounded-lg border border-dark-500/50 hover:border-drilling-500/50 transition-all text-center"
              style={{ background: `${risk > 0.5 ? RISK_COLORS.high : risk > 0.3 ? RISK_COLORS.warning : RISK_COLORS.normal}15` }}
            >
              <div className="text-[10px] text-gray-400">{well.replace('WELL-', 'W-')}</div>
              <div className="text-xs font-bold mt-0.5" style={{ color: risk > 0.5 ? RISK_COLORS.high : risk > 0.3 ? RISK_COLORS.warning : RISK_COLORS.normal }}>
                {(risk * 100).toFixed(0)}%
              </div>
            </button>
          ))}
        </div>
      </motion.div>
    </div>
  );
}

function generateMockData() {
  const wells = {};
  for (let i = 1; i <= 20; i++) {
    wells[`WELL-${String(i).padStart(3, '0')}`] = Math.random() * 0.6 + 0.1;
  }
  return {
    total_wells: 20,
    high_risk_wells: 4,
    active_alerts: 12,
    average_stuck_risk: 0.28,
    max_risk: 0.92,
    drilling_instability_index: 0.35,
    well_risk_scores: wells,
    risk_distribution: { critical: 2400, high: 5200, warning: 12000, low: 45000, normal: 235400 },
    alert_summary: { CRITICAL: 3, HIGH_RISK: 8, WARNING: 15, LOW_RISK: 22, NORMAL: 0 },
  };
}
