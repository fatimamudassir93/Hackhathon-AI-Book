import React from 'react';
import { AuthProvider } from '../context/AuthContext';
import Chatbot from '../components/Chatbot';

// Default implementation, that you can customize
export default function Root({ children }) {
  return (
    <AuthProvider>
      {children}
      <Chatbot />
    </AuthProvider>
  );
}
