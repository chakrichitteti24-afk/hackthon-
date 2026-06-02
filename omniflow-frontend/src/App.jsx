import { useMemo, useState, useEffect } from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import Header from './components/Header.jsx';
import Sidebar from './components/Sidebar.jsx';
import { AppContext } from './context/AppContext.js';
import ChatPage from './pages/ChatPage.jsx';
import DashboardPage from './pages/DashboardPage.jsx';
import CustomerMemoryPage from './pages/CustomerMemoryPage.jsx';

const createUserId = () => {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return `user_${crypto.randomUUID().slice(0, 8)}`;
  }
  return `user_${Date.now()}_${Math.random().toString(36).slice(2, 6)}`;
};

export default function App() {
  const [userId, setUserId] = useState(() => {
    const active = localStorage.getItem('omniflow_active_user');
    if (active) return active;
    const newId = createUserId();
    localStorage.setItem('omniflow_active_user', newId);
    return newId;
  });
  
  const [currentAgent, setCurrentAgent] = useState('sales');

  // Track all user sessions in local storage
  useEffect(() => {
    try {
      const saved = localStorage.getItem('omniflow_sessions');
      const sessions = saved ? JSON.parse(saved) : [];
      if (!sessions.includes(userId)) {
        sessions.push(userId);
        localStorage.setItem('omniflow_sessions', JSON.stringify(sessions));
      }
      localStorage.setItem('omniflow_active_user', userId);
    } catch (e) {
      console.error('Error tracking session ID in App.jsx:', e);
    }
  }, [userId]);

  const contextValue = useMemo(
    () => ({
      userId,
      setUserId,
      currentAgent,
      setCurrentAgent,
    }),
    [userId, currentAgent],
  );

  return (
    <AppContext.Provider value={contextValue}>
      <BrowserRouter>
        <div className="min-h-screen bg-bg text-text font-sans select-none flex">
          <Sidebar />
          <div className="flex min-w-0 flex-1 flex-col">
            <Header />
            <main className="flex-1 overflow-auto bg-bg">
              <Routes>
                <Route path="/" element={<ChatPage />} />
                <Route path="/dashboard" element={<DashboardPage />} />
                <Route path="/customer-memory" element={<CustomerMemoryPage />} />
              </Routes>
            </main>
          </div>
        </div>
      </BrowserRouter>
    </AppContext.Provider>
  );
}
