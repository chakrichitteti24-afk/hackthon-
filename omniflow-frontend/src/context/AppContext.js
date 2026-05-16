import { createContext } from 'react';

export const AppContext = createContext({
  userId: '',
  currentAgent: 'sales',
  setCurrentAgent: () => {},
});
