import axios from "axios";

const API_BASE = "http://localhost:8000/api/v1";

export const api = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
    }
    return Promise.reject(err);
  }
);

export const authAPI = {
  login: (username: string, password: string) =>
    api.post("/auth/login", { username, password }).then((r) => r.data),
};

export const gridAPI = {
  getState: () => api.get("/grid/state").then((r) => r.data),
  getComponents: () => api.get("/grid/components").then((r) => r.data),
  simulate: () => api.post("/grid/simulate").then((r) => r.data),
  getHistory: (limit = 50) => api.get(`/grid/history?limit=${limit}`).then((r) => r.data),
};

export const sensorAPI = {
  list: (limit = 100) => api.get(`/sensors?limit=${limit}`).then((r) => r.data),
  getReadings: (sensorId: string, limit = 100) =>
    api.get(`/sensors/${sensorId}/readings?limit=${limit}`).then((r) => r.data),
};

export const faultAPI = {
  list: (activeOnly = false) =>
    api.get(`/faults?active_only=${activeOnly}`).then((r) => r.data),
  get: (faultId: string) => api.get(`/faults/${faultId}`).then((r) => r.data),
  inject: (data: {
    component_id: string;
    fault_type: string;
    severity: number;
    duration?: number;
  }) => api.post("/faults/inject", data).then((r) => r.data),
  reset: () => api.post("/faults/reset").then((r) => r.data),
};

export const recoveryAPI = {
  listPlans: (faultId?: string) =>
    api.get(`/recovery/plans${faultId ? `?fault_id=${faultId}` : ""}`).then((r) => r.data),
  getPlan: (planId: string) => api.get(`/recovery/plans/${planId}`).then((r) => r.data),
  execute: (planId: string) =>
    api.post("/recovery/execute", { plan_id: planId }).then((r) => r.data),
  autoRecover: (faultId: string) =>
    api.post(`/recovery/auto-recover/${faultId}`).then((r) => r.data),
};

export const aiAPI = {
  getPredictions: (limit = 50) => api.get(`/ai/predictions?limit=${limit}`).then((r) => r.data),
  getLocalizations: (limit = 50) => api.get(`/ai/localizations?limit=${limit}`).then((r) => r.data),
};

export const analyticsAPI = {
  summary: () => api.get("/analytics/summary").then((r) => r.data),
  faultDistribution: () => api.get("/analytics/fault-distribution").then((r) => r.data),
  vulnerable: () => api.get("/analytics/vulnerable-components").then((r) => r.data),
  recentEvents: (limit = 50) => api.get(`/analytics/recent-events?limit=${limit}`).then((r) => r.data),
};
