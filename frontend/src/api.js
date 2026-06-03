import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

export const getDashboardSummary = () => api.get('/dashboard/summary');
export const getWellDetail = (wellId, limit = 500) => api.get(`/well/${wellId}?limit=${limit}`);
export const getAlerts = (severity, wellId, limit = 50) => {
  const params = new URLSearchParams();
  if (severity) params.append('severity', severity);
  if (wellId) params.append('well_id', wellId);
  params.append('limit', limit);
  return api.get(`/alerts?${params}`);
};
export const predictStuckPipe = (data) => api.post('/predict/stuck-pipe', data);
export const getRiskPredictions = (wellId, limit = 100) => api.get(`/predict/risk?well_id=${wellId}&limit=${limit}`);
export const getRecommendation = (data) => api.post('/recommendation', data);
export const explainRisk = (wellId) => api.get(`/explain-risk?well_id=${wellId}`);
export const healthCheck = () => api.get('/health');

export default api;
