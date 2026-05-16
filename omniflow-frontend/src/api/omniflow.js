import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8001';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
});

const getErrorMessage = (error) => {
  if (error.code === 'ERR_NETWORK') {
    return `Backend is offline at ${API_BASE}. Start FastAPI on port 8000 and try again.`;
  }

  return error.response?.data?.detail || error.message || 'Request failed.';
};

export const postChat = async (userId, message, agentType) => {
  try {
    const response = await api.post('/chat', {
      user_id: userId,
      message,
      agent_type: agentType,
    });
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error), { cause: error });
  }
};

export const getSession = async (userId) => {
  try {
    const response = await api.get(`/session/${userId}`);
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error), { cause: error });
  }
};

export const postEscalate = async (userId) => {
  try {
    const response = await api.post(`/escalate/${userId}`);
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error), { cause: error });
  }
};

export const checkHealth = async () => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error), { cause: error });
  }
};
