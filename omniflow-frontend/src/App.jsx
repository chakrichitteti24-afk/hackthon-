import { useMemo, useState } from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import Header from './components/Header.jsx';
import Sidebar from './components/Sidebar.jsx';
import { AppContext } from './context/AppContext.js';
import ChatPage from './pages/ChatPage.jsx';
import DashboardPage from './pages/DashboardPage.jsx';

const createUserId = () => {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return `user_${crypto.randomUUID()}`;
  }

  return `user_${Date.now()}_${Math.random().toString(36).slice(2, 10)}`;
};

export default function App() {
  const [userId] = useState(createUserId);
  const [currentAgent, setCurrentAgent] = useState('sales');

  const contextValue = useMemo(
    () => ({
      userId,
      currentAgent,
      setCurrentAgent,
    }),
    [userId, currentAgent],
  );

  return (
    <AppContext.Provider value={contextValue}>
      <BrowserRouter>
        <div className="min-h-screen bg-bg text-primary font-mono">
          <div className="flex min-h-screen">
            <Sidebar />
            <div className="flex min-w-0 flex-1 flex-col">
              <Header />
              <main className="flex-1 overflow-auto p-4 sm:p-6">
                <Routes>
                  <Route path="/" element={<ChatPage />} />
                  <Route path="/dashboard" element={<DashboardPage />} />
                </Routes>
              </main>
            </div>
          </div>
        </div>
      </BrowserRouter>
    </AppContext.Provider>
  );
}
