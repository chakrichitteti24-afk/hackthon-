import { createContext } from 'react';

export const AppContext = createContext({
  userId: '',
  setUserId: () => {},
  currentAgent: 'sales',
  setCurrentAgent: () => {},
});
