import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar, PieChart, Pie, Cell, Legend
} from 'recharts'

const COLORS = ['#00d4ff', '#00ff88', '#ff8800', '#ff3366', '#a855f7']

export function RiskAreaChart({ data, dataKey = 'risk', title }) {
  return (
    <div className="glass-card p-6">
      <h3 className="text-sm font-medium text-gray-400 mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={250}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="riskGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#ff3366" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#ff3366" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#243049" />
          <XAxis dataKey="name" stroke="#6b7280" fontSize={11} />
          <YAxis stroke="#6b7280" fontSize={11} />
          <Tooltip
            contentStyle={{ background: '#1a2035', border: '1px solid #243049', borderRadius: '8px' }}
            labelStyle={{ color: '#9ca3af' }}
          />
          <Area type="monotone" dataKey={dataKey} stroke="#ff3366" fill="url(#riskGradient)" strokeWidth={2} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}

export function RiskBarChart({ data, title }) {
  return (
    <div className="glass-card p-6">
      <h3 className="text-sm font-medium text-gray-400 mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={250}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#243049" />
          <XAxis dataKey="name" stroke="#6b7280" fontSize={11} />
          <YAxis stroke="#6b7280" fontSize={11} />
          <Tooltip
            contentStyle={{ background: '#1a2035', border: '1px solid #243049', borderRadius: '8px' }}
          />
          <Bar dataKey="value" radius={[4, 4, 0, 0]}>
            {data.map((entry, index) => (
              <Cell key={index} fill={COLORS[index % COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

export function RiskPieChart({ data, title }) {
  return (
    <div className="glass-card p-6">
      <h3 className="text-sm font-medium text-gray-400 mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={250}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={90}
            paddingAngle={3}
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={index} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Legend
            wrapperStyle={{ fontSize: '12px', color: '#9ca3af' }}
          />
          <Tooltip
            contentStyle={{ background: '#1a2035', border: '1px solid #243049', borderRadius: '8px' }}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}
