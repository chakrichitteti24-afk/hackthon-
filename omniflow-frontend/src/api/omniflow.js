import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8001';
const OFFLINE_RETRY_MS = 5000;

let backendOfflineUntil = 0;

const api = axios.create({
  baseURL: API_BASE,
  timeout:90000,
});

const createApiError = (message, cause) => {
  const error = new Error(message);
  if (cause) {
    error.cause = cause;
  }
  return error;
};

const getOfflineMessage = () =>
  `Backend is offline at ${API_BASE}. Start FastAPI on port 8001 and try again.`;

const getErrorMessage = (error) => {
  if (error.code === 'ERR_NETWORK') {
    return getOfflineMessage();
  }

  return error.response?.data?.detail || error.message || 'Request failed.';
};

const request = async (callback) => {
  if (backendOfflineUntil > Date.now()) {
    throw createApiError(getOfflineMessage());
  }

  try {
    const response = await callback();
    backendOfflineUntil = 0;
    return response.data;
  } catch (error) {
    if (error.code === 'ERR_NETWORK') {
      backendOfflineUntil = Date.now() + OFFLINE_RETRY_MS;
    }
    throw createApiError(getErrorMessage(error), error);
  }
};

export const postChat = async (userId, message, agentType) => {
  return request(() =>
    api.post('/chat', {
      user_id: userId,
      message,
      agent_type: agentType,
    })
  );
};

export const getSession = async (userId) => {
  return request(() => api.get(`/session/${userId}`));
};

export const postEscalate = async (userId) => {
  return request(() => api.post(`/escalate/${userId}`));
};

export const checkHealth = async () => {
  return request(() => api.get('/health'));
};

export const getActivities = async (userId) => {
  return request(() => api.get(`/activities/${userId}`));
};

export const postDemo = async (scenario, userId) => {
  return request(() => api.post(`/demo/${scenario}/${userId}`));
};

export const getStatus = async () => {
  return request(() => api.get('/status'));
};

export const getAnalytics = async () => {
  return request(() => api.get('/analytics'));
};
