import { useQuery } from '@tanstack/react-query';
import { fetchRequests } from '../api/client';
import { Link } from 'react-router-dom';
import { Search } from 'lucide-react';

export default function Requests() {
  const { data: requests, isLoading } = useQuery({ queryKey: ['requests'], queryFn: fetchRequests });

  if (isLoading) return <div className="animate-pulse bg-white border border-gray-200 rounded-xl h-64 w-full"></div>;

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-semibold text-gray-900 tracking-tight">Requests</h1>
        <div className="flex items-center gap-4">
          <div className="relative">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input type="text" placeholder="Search requests..." className="pl-9 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-64" />
          </div>
          <Link to="/requests/new" className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors whitespace-nowrap">
            + New Purchase Request
          </Link>
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden">
        <table className="w-full text-left text-sm whitespace-nowrap">
          <thead className="bg-gray-50 text-gray-500 font-medium border-b border-gray-200">
            <tr>
              <th className="px-6 py-3">Request ID</th>
              <th className="px-6 py-3">User</th>
              <th className="px-6 py-3">Date</th>
              <th className="px-6 py-3 text-right">Amount</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {requests?.map((r: any) => (
              <tr key={r.request_id} className="hover:bg-gray-50 group">
                <td className="px-6 py-4">
                  <Link to={`/requests/${r.request_id}`} className="font-medium text-blue-600 group-hover:underline">
                    {r.request_text ? (
                      <div className="flex flex-col">
                        <span className="text-gray-900">{r.request_text}</span>
                        <span className="text-xs text-gray-500 font-normal">{r.request_id}</span>
                      </div>
                    ) : r.request_id}
                  </Link>
                </td>
                <td className="px-6 py-4 text-gray-500">{r.user_id}</td>
                <td className="px-6 py-4 text-gray-500">{r.request_date || 'N/A'}</td>
                <td className="px-6 py-4 text-right font-medium text-gray-900">₹{r.requested_amount.toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
