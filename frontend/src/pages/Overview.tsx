import { useQuery } from '@tanstack/react-query';
import { fetchRequests } from '../api/client';
import { Link } from 'react-router-dom';

export default function Overview() {
  const { data: requests, isLoading } = useQuery({ queryKey: ['requests'], queryFn: fetchRequests });

  if (isLoading) return <div className="animate-pulse flex gap-4"><div className="w-64 h-32 bg-gray-200 rounded-xl"></div></div>;

  return (
    <div className="flex flex-col gap-8">
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900 tracking-tight">Financial Overview</h1>
          <p className="text-sm text-gray-500 mt-1">Monitor affordability decisions and system safety metrics.</p>
        </div>
        <Link to="/requests/new" className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
          + New Purchase Request
        </Link>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
          <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Total Requests</div>
          <div className="text-3xl font-semibold text-gray-900">{requests?.length || 0}</div>
        </div>
        <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
          <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Avg Request</div>
          <div className="text-3xl font-semibold text-gray-900">
            ₹{requests ? Math.round(requests.reduce((a:any, b:any) => a + b.requested_amount, 0) / requests.length).toLocaleString() : 0}
          </div>
        </div>
      </div>

      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Requests</h2>
        <div className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden">
          <table className="w-full text-left text-sm whitespace-nowrap">
            <thead className="bg-gray-50 text-gray-500 font-medium border-b border-gray-200">
              <tr>
                <th className="px-6 py-3">Request ID</th>
                <th className="px-6 py-3">User</th>
                <th className="px-6 py-3 text-right">Amount</th>
                <th className="px-6 py-3"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {requests?.slice(0, 10).map((r: any) => (
                <tr key={r.request_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 font-medium text-gray-900">
                    {r.request_text ? (
                      <div className="flex flex-col">
                        <span className="text-gray-900">{r.request_text}</span>
                        <span className="text-xs text-gray-500 font-normal">{r.request_id}</span>
                      </div>
                    ) : r.request_id}
                  </td>
                  <td className="px-6 py-4 text-gray-500">{r.user_id}</td>
                  <td className="px-6 py-4 text-right text-gray-900">₹{r.requested_amount.toLocaleString()}</td>
                  <td className="px-6 py-4 text-right">
                    <Link to={`/requests/${r.request_id}`} className="text-blue-600 hover:text-blue-800 font-medium">Evaluate &rarr;</Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
