/**
 * lib/api.js — Centralized Axios API client
 * Handles: auth headers, token refresh, error formatting
 */

import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8001";

const client = axios.create({ baseURL: BASE_URL, timeout: 90000 });

// Attach token to every request
client.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Handle 401 → redirect to login
client.interceptors.response.use(
  (res) => res.data,
  async (error) => {
    const message =
      error.response?.data?.error ||
      error.response?.data?.detail?.[0]?.msg ||
      error.message ||
      "Something went wrong";

    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }

    return Promise.reject(new Error(message));
  }
);

// ── Auth ─────────────────────────────────────────────────────────────────────
export const authApi = {
  signup: (data) => client.post("/auth/signup", data),
  login: (data) => client.post("/auth/login", data),
  verifyEmail: (token) => client.get(`/auth/verify/${token}`),
  forgotPassword: (email) => client.post("/auth/forgot-password", { email }),
  resetPassword: (data) => client.post("/auth/reset-password", data),
  changePassword: (data) => client.post("/auth/change-password", data),
  getMe: () => client.get("/auth/me"),
  updateProfile: (data) => client.patch("/auth/me", data),
  deleteAccount: () => client.delete("/auth/me"),
};

// ── Projects ──────────────────────────────────────────────────────────────────
export const projectApi = {
  upload: (file, onProgress) => {
    const form = new FormData();
    form.append("file", file);
    return client.post("/projects/upload", form, {
      headers: { "Content-Type": "multipart/form-data" },
      onUploadProgress: (e) => onProgress?.(Math.round((e.loaded * 100) / e.total)),
    });
  },
  list: () => client.get("/projects/"),
  get: (id) => client.get(`/projects/${id}`),
  delete: (id) => client.delete(`/projects/${id}`),
  dashboardStats: () => client.get("/projects/dashboard/stats"),
};

// ── Analysis ──────────────────────────────────────────────────────────────────
export const analysisApi = {
  getQuality: (id) => client.get(`/analyze/quality/${id}`),
  clean: (id, strategy) => client.post(`/analyze/clean/${id}`, { project_id: id, strategy }),
  getEDA: (id) => client.get(`/analyze/eda/${id}`),
  getCharts: (id) => client.get(`/analyze/charts/${id}`),
  getForecast: (id, payload) => client.post(`/analyze/forecast/${id}`, payload),
  getInsights: (id) => client.get(`/analyze/insights/${id}`),
  getRecommendations: (id) => client.get(`/analyze/recommendations/${id}`),
  getDashboard: (id) => client.get(`/analyze/dashboard/${id}`),
  generateReport: (id, format) => client.post(`/analyze/report/${id}`, { project_id: id, format }),
  downloadReport: (filename) => `${BASE_URL}/analyze/download/report/${filename}`,
  downloadDataset: (id) => `${BASE_URL}/analyze/download/dataset/${id}`,
};

// ── Chat ──────────────────────────────────────────────────────────────────────
export const chatApi = {
  send: (projectId, message) =>
    client.post(`/chat/${projectId}`, { project_id: projectId, message }),
  getHistory: (projectId) => client.get(`/chat/${projectId}/history`),
  clearHistory: (projectId) => client.delete(`/chat/${projectId}/history`),
  streamUrl: (projectId) => `${BASE_URL}/chat/${projectId}/stream`,
};

export default client;
