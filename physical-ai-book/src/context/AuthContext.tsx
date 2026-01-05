import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { getApiUrl } from '../utils/apiConfig';

interface UserProfile {
  technical_level: string;
  programming_experience: string[];
  robotics_background: string;
  learning_goals: string;
  preferred_language: string;
}

interface User {
  id: string;
  email: string;
  name?: string;
  profile?: UserProfile;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  signup: (userData: SignupData) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

interface SignupData {
  email: string;
  password: string;
  name?: string;
  technical_level: string;
  programming_experience: string[];
  robotics_background: string;
  learning_goals?: string;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  // Get API URL from configuration
  const API_URL = getApiUrl();
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Load token from localStorage on mount
  useEffect(() => {
    // Only access localStorage in browser environment
    if (typeof window !== 'undefined') {
      const storedToken = localStorage.getItem('auth_token');
      if (storedToken) {
        setToken(storedToken);
        fetchUserProfile(storedToken);
      } else {
        setIsLoading(false);
      }
    } else {
      setIsLoading(false);
    }
  }, []);

  const fetchUserProfile = async (authToken: string) => {
    try {
      const response = await fetch(`${API_URL}/api/auth/me`, {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      } else {
        // Token invalid, clear it
        if (typeof window !== 'undefined') {
          localStorage.removeItem('auth_token');
        }
        setToken(null);
      }
    } catch (error) {
      console.error('Error fetching user profile:', error);
      localStorage.removeItem('auth_token');
      setToken(null);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    try {
      const response = await fetch(`${API_URL}/api/auth/signin`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Login failed');
      }

      const data = await response.json();
      const newToken = data.access_token;

      if (typeof window !== 'undefined') {
        localStorage.setItem('auth_token', newToken);
      }
      setToken(newToken);
      await fetchUserProfile(newToken);
    } catch (error) {
      throw error;
    }
  };

  const signup = async (userData: SignupData) => {
    try {
      const response = await fetch(`${API_URL}/api/auth/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData)
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Signup failed');
      }

      const data = await response.json();
      const newToken = data.access_token;

      if (typeof window !== 'undefined') {
        localStorage.setItem('auth_token', newToken);
      }
      setToken(newToken);
      await fetchUserProfile(newToken);
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
    }
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, login, signup, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
