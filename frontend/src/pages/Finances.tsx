import { useQuery } from '@tanstack/react-query';
import { fetchUser } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';

export default function Finances() {
  const { userId } = useAuth();
  
  const { data: user, isLoading } = useQuery({ 
    queryKey: ['user', userId], 
    queryFn: () => fetchUser(userId!),
    enabled: !!userId
  });

  if (isLoading) return <div className="animate-pulse bg-gray-200 h-64 rounded-xl"></div>;

  if (!user) {
    return (
      <div className="flex flex-col items-center justify-center h-64 border-2 border-dashed border-gray-300 rounded-xl bg-gray-50">
        <p className="text-gray-500 mb-4">Complete your financial profile before viewing finances.</p>
        <Link to="/onboarding" className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium">Finish setup &rarr;</Link>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-8 max-w-4xl">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900 tracking-tight">My Finances</h1>
        <p className="text-sm text-gray-500 mt-1">Your core financial profile and commitments.</p>
      </div>

      <div className="bg-white border border-gray-200 rounded-2xl shadow-sm overflow-hidden flex flex-col md:flex-row">
        <div className="p-8 md:w-1/2 border-b md:border-b-0 md:border-r border-gray-100">
          <div className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">Current Balance</div>
          <div className="text-4xl font-semibold text-gray-900 tracking-tight mb-6">
            ₹{user.current_balance.toLocaleString()}
          </div>
          
          <div className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">Minimum To Keep</div>
          <div className="text-2xl font-medium text-gray-900 mb-2">
            ₹{user.minimum_balance.toLocaleString()}
          </div>
        </div>
        
        <div className="p-8 md:w-1/2 bg-gray-50">
          <div className="flex flex-col gap-6">
            <div>
              <div className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-2">Profile Overview</div>
              <div className="flex justify-between py-2 border-b border-gray-200">
                <span className="text-gray-600">Home Currency</span>
                <span className="font-medium text-gray-900">{user.home_currency}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-gray-200">
                <span className="text-gray-600">Active Commitments</span>
                <span className="font-medium text-gray-900">{user.active_events_count} active</span>
              </div>
            </div>
            
            <button className="w-full py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50">
              Edit Financial Profile
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
