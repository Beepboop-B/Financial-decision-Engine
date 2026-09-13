import { createContext, useContext, useState, useEffect } from 'react';

interface AuthContextType {
  userId: string | null;
  login: (id: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [userId, setUserId] = useState<string | null>(null);

  useEffect(() => {
    const saved = localStorage.getItem('bw_user_id');
    if (saved) setUserId(saved);
  }, []);

  const login = (id: string) => {
    setUserId(id);
    localStorage.setItem('bw_user_id', id);
  };

  const logout = () => {
    setUserId(null);
    localStorage.removeItem('bw_user_id');
  };

  return (
    <AuthContext.Provider value={{ userId, login, logout }}>
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
