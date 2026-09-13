import { useQuery } from '@tanstack/react-query';
import { fetchUser, fetchUserPurchases } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { Link, useNavigate } from 'react-router-dom';

export default function Home() {
  const { userId } = useAuth();
  const navigate = useNavigate();

  // If no user is logged in, redirect to DemoSelector/Onboarding
  if (!userId) {
    navigate('/demo');
    return null;
  }

  const { data: user, isLoading: userLoading } = useQuery({ 
    queryKey: ['user', userId], 
    queryFn: () => fetchUser(userId),
    enabled: !!userId
  });

  const { data: purchases, isLoading: purchasesLoading } = useQuery({
    queryKey: ['user_purchases', userId],
    queryFn: () => fetchUserPurchases(userId),
    enabled: !!userId
  });

  if (userLoading || purchasesLoading) return <div className="animate-pulse flex gap-4"><div className="w-full h-32 bg-gray-200 rounded-xl"></div></div>;

  if (!user) {
    return (
      <div className="flex flex-col items-center justify-center h-64 border-2 border-dashed border-gray-300 rounded-xl bg-gray-50">
        <p className="text-gray-500 mb-4">Complete your financial profile before evaluating a purchase.</p>
        <Link to="/onboarding" className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium">Finish setup &rarr;</Link>
      </div>
    );
  }

  const safeBuffer = user.current_balance - user.minimum_balance;

  return (
    <div className="flex flex-col gap-10">
      <div>
        <h1 className="text-3xl font-semibold text-gray-900 tracking-tight">Good morning</h1>
        <p className="text-gray-500 mt-2">Your finances are ready.</p>
      </div>

      <div className="grid md:grid-cols-3 gap-4">
        <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
          <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Current Balance</div>
          <div className="text-3xl font-semibold text-gray-900">₹{user.current_balance.toLocaleString()}</div>
        </div>
        <div className="bg-white border border-gray-200 rounded-2xl p-6 shadow-sm">
          <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Safe Buffer</div>
          <div className="text-3xl font-semibold text-green-600">₹{safeBuffer > 0 ? safeBuffer.toLocaleString() : 0}</div>
        </div>
        <div className="bg-blue-600 border border-blue-700 rounded-2xl p-6 shadow-sm text-white flex flex-col items-start justify-center relative overflow-hidden group">
          <div className="relative z-10">
            <div className="text-blue-200 text-sm font-medium mb-1">Check whether you can safely afford something.</div>
          </div>
          <Link to="/purchases/new" className="relative z-10 mt-4 bg-white text-blue-600 px-4 py-2 rounded-lg font-semibold shadow-sm group-hover:bg-blue-50 transition-colors">
            + New Purchase
          </Link>
          <div className="absolute right-[-20px] bottom-[-20px] opacity-10">
            <svg width="120" height="120" viewBox="0 0 24 24" fill="currentColor"><path d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z"></path></svg>
          </div>
        </div>
      </div>

      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Purchases</h2>
        
        {!purchases || purchases.length === 0 ? (
          <div className="bg-white border border-gray-200 rounded-2xl p-8 text-center">
            <p className="text-gray-500 mb-4">No purchases yet.</p>
            <Link to="/purchases/new" className="text-blue-600 font-medium hover:underline">Check your first purchase &rarr;</Link>
          </div>
        ) : (
          <div className="bg-white border border-gray-200 rounded-xl shadow-sm overflow-hidden">
            <table className="w-full text-left text-sm whitespace-nowrap">
              <thead className="bg-gray-50 text-gray-500 font-medium border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3">Purchase</th>
                  <th className="px-6 py-3">Date</th>
                  <th className="px-6 py-3 text-right">Amount</th>
                  <th className="px-6 py-3"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {purchases.slice(0, 5).map((r: any) => (
                  <tr key={r.request_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 font-medium text-gray-900">
                      {r.request_text ? (
                        <div className="flex flex-col">
                          <span className="text-gray-900">{r.request_text}</span>
                        </div>
                      ) : 'Purchase Request'}
                    </td>
                    <td className="px-6 py-4 text-gray-500">{r.request_date}</td>
                    <td className="px-6 py-4 text-right text-gray-900">₹{r.requested_amount.toLocaleString()}</td>
                    <td className="px-6 py-4 text-right">
                      <Link to={`/requests/${r.request_id}`} className="text-blue-600 hover:text-blue-800 font-medium">View Result &rarr;</Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
