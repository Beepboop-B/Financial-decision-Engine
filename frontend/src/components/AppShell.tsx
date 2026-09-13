import { NavLink, useNavigate } from 'react-router-dom';
import { Activity, Home, Wallet, ShoppingBag, LayoutDashboard, Terminal, LogOut } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { fetchHealth } from '../api/client';
import { useAuth } from '../context/AuthContext';

export function AppShell({ children }: { children: React.ReactNode }) {
  const { data: health } = useQuery({ queryKey: ['health'], queryFn: fetchHealth });
  const { userId, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/demo');
  };

  return (
    <div className="flex h-screen w-full bg-[#f9fafb]">
      {/* Sidebar */}
      <aside className="w-64 flex flex-col border-r border-gray-200 bg-white">
        <div className="h-16 flex items-center px-6 border-b border-gray-200">
          <div className="font-bold text-lg tracking-tight text-gray-900 flex items-center gap-2">
            <div className="w-6 h-6 rounded bg-blue-600"></div>
            Buy or Wait
          </div>
        </div>
        <nav className="flex-1 py-4 px-3 flex flex-col gap-1 overflow-y-auto">
          <div className="px-3 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 mt-2">Personal</div>
          <NavLink to="/home" className={({isActive}) => `flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium ${isActive ? 'bg-gray-100 text-gray-900' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'}`}>
            <Home size={18} /> Home
          </NavLink>
          <NavLink to="/finances" className={({isActive}) => `flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium ${isActive ? 'bg-gray-100 text-gray-900' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'}`}>
            <Wallet size={18} /> My Finances
          </NavLink>
          <NavLink to="/purchases" className={({isActive}) => `flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium ${isActive ? 'bg-gray-100 text-gray-900' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'}`}>
            <ShoppingBag size={18} /> Purchases
          </NavLink>
          
          <div className="px-3 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 mt-6">System / Developer</div>
          <NavLink to="/demo" className={({isActive}) => `flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium ${isActive ? 'bg-gray-100 text-gray-900' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'}`}>
            <LayoutDashboard size={18} /> Demo Mode
          </NavLink>
          <NavLink to="/system/usage" className={({isActive}) => `flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium ${isActive ? 'bg-gray-100 text-gray-900' : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'}`}>
            <Activity size={18} /> Usage
          </NavLink>
          <div className="flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium text-gray-400 cursor-not-allowed">
            <Terminal size={18} /> Trace
          </div>
        </nav>
        
        <div className="p-4 border-t border-gray-200">
          <div className="flex items-center gap-2 text-xs font-medium text-gray-500">
            <div className={`w-2 h-2 rounded-full ${health?.mode === 'live' ? 'bg-green-500' : 'bg-amber-500'}`}></div>
            {health ? `Mode: ${health.mode.toUpperCase()}` : 'Connecting...'}
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden relative">
        {/* Banner for demo mode */}
        {userId && userId !== 'user_01' && userId.includes('_') && (
          <div className="bg-amber-100 text-amber-800 text-xs font-semibold px-4 py-1.5 flex justify-center items-center">
            DEMO USER MODE ACTIVE ({userId})
          </div>
        )}
        <header className="h-16 flex items-center justify-between px-8 border-b border-gray-200 bg-white shrink-0">
          <div className="text-sm font-medium text-gray-500">
            Financial Decision Intelligence
          </div>
          <div className="flex items-center gap-4">
            {userId && (
              <>
                <span className="text-sm font-medium text-gray-700">{userId}</span>
                <button onClick={handleLogout} className="text-gray-500 hover:text-gray-900">
                  <LogOut size={16} />
                </button>
              </>
            )}
            <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center font-bold text-sm border border-blue-200">
              {userId ? userId.charAt(0).toUpperCase() : '?'}
            </div>
          </div>
        </header>
        <div className="flex-1 overflow-auto p-8">
          <div className="max-w-6xl mx-auto">
            {children}
          </div>
        </div>
      </main>
    </div>
  );
}
