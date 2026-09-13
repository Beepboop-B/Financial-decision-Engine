import { useQuery } from '@tanstack/react-query';
import { fetchUserPurchases } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';
import { Search } from 'lucide-react';

export default function Purchases() {
  const { userId } = useAuth();
  
  const { data: purchases, isLoading } = useQuery({ 
    queryKey: ['user_purchases', userId], 
    queryFn: () => fetchUserPurchases(userId!),
    enabled: !!userId
  });

  if (isLoading) return <div className="animate-pulse bg-white border border-gray-200 rounded-xl h-64 w-full"></div>;

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900 tracking-tight">Purchase History</h1>
          <p className="text-sm text-gray-500 mt-1">Your past evaluations and decisions.</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="relative">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input type="text" placeholder="Search purchases..." className="pl-9 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-64" />
          </div>
          <Link to="/purchases/new" className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap">
            + New Purchase
          </Link>
        </div>
      </div>

      {!purchases || purchases.length === 0 ? (
        <div className="bg-white border border-gray-200 rounded-2xl p-12 text-center mt-4">
          <div className="w-16 h-16 bg-blue-50 text-blue-600 rounded-2xl mx-auto flex items-center justify-center mb-4">
            <Search size={24} />
          </div>
          <h2 className="text-lg font-semibold text-gray-900 mb-2">No purchases yet</h2>
          <p className="text-gray-500 mb-6 max-w-md mx-auto">You haven't evaluated any purchases yet. Create a new purchase request to see if you can afford it.</p>
          <Link to="/purchases/new" className="bg-blue-600 text-white px-6 py-2.5 rounded-lg font-medium inline-block">
            Create First Purchase
          </Link>
        </div>
      ) : (
        <div className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden mt-2">
          <table className="w-full text-left text-sm whitespace-nowrap">
            <thead className="bg-gray-50 text-gray-500 font-medium border-b border-gray-200">
              <tr>
                <th className="px-6 py-3">Item</th>
                <th className="px-6 py-3">Date</th>
                <th className="px-6 py-3 text-right">Amount</th>
                <th className="px-6 py-3"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {purchases.map((r: any) => (
                <tr key={r.request_id} className="hover:bg-gray-50 group">
                  <td className="px-6 py-4">
                    <Link to={`/requests/${r.request_id}`} className="flex flex-col group-hover:underline">
                      <span className="font-medium text-gray-900">{r.request_text || 'Purchase Request'}</span>
                      <span className="text-xs text-gray-400 mt-0.5">{r.request_id}</span>
                    </Link>
                  </td>
                  <td className="px-6 py-4 text-gray-500">{r.request_date || 'N/A'}</td>
                  <td className="px-6 py-4 text-right font-medium text-gray-900">₹{r.requested_amount.toLocaleString()}</td>
                  <td className="px-6 py-4 text-right">
                    <Link to={`/requests/${r.request_id}`} className="text-blue-600 hover:text-blue-800 font-medium">View &rarr;</Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
