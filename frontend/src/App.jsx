import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import WellDetail from './pages/WellDetail'
import AIInsights from './pages/AIInsights'
import AlertCenter from './pages/AlertCenter'
import Optimization from './pages/Optimization'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="well/:wellId" element={<WellDetail />} />
          <Route path="insights" element={<AIInsights />} />
          <Route path="alerts" element={<AlertCenter />} />
          <Route path="optimization" element={<Optimization />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
