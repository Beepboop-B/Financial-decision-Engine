import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { evaluateRequest, fetchRequestDetail } from '../api/client';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Info } from 'lucide-react';

export default function RequestDetail() {
  const { id } = useParams<{ id: string }>();

  const { data: req, isLoading: reqLoading } = useQuery({ 
    queryKey: ['request', id], 
    queryFn: () => fetchRequestDetail(id!)
  });

  const { data: decision, isLoading: decLoading } = useQuery({ 
    queryKey: ['decision', id], 
    queryFn: () => evaluateRequest(id!)
  });

  if (reqLoading || decLoading) return <div className="animate-pulse h-64 bg-gray-200 rounded-xl"></div>;
  if (!decision || !req) return <div>Failed to load.</div>;

  const isSafeNow = decision.affordability_status === 'affordable_now';
  const isSafeWithPlan = decision.affordability_status === 'affordable_with_plan';
  const statusColor = isSafeNow ? 'bg-green-100 text-green-700 border-green-200' : isSafeWithPlan ? 'bg-amber-100 text-amber-700 border-amber-200' : 'bg-red-100 text-red-700 border-red-200';

  // Format chart data
  const chartData = decision.trace?.checkpoints?.map((c: any) => ({
    date: c.date,
    balance: c.balance_start,
    min: c.min_balance
  })) || [];

  return (
    <div className="flex flex-col gap-8 pb-12">
      {/* Header */}
      <div className="flex flex-col mb-4 border-b border-gray-100 pb-6">
        <div className="text-sm text-gray-500 uppercase tracking-wider font-semibold mb-2">Can I afford this?</div>
        <div className="flex justify-between items-end">
          <div>
            <h1 className="text-3xl font-semibold text-gray-900 tracking-tight">
              {req.request_text ? `${req.request_text}` : 'Purchase'}
            </h1>
            <div className="text-xl text-gray-500 mt-1">₹{req.requested_amount.toLocaleString()}</div>
          </div>
          <div className={`px-4 py-2 rounded-lg border text-sm font-semibold uppercase tracking-wider ${statusColor}`}>
            {decision.affordability_status.replace(/_/g, ' ')}
          </div>
        </div>
      </div>

      {/* Decision Card */}
      <div className="bg-white border border-gray-200 shadow-sm rounded-2xl overflow-hidden flex flex-col md:flex-row">
        <div className="p-8 md:w-1/2 border-b md:border-b-0 md:border-r border-gray-100 flex flex-col justify-center">
          <div className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4">Safe To Pay Today</div>
          <div className="text-5xl font-semibold text-gray-900 tracking-tight mb-2">
            ₹{decision.amount_safe_to_pay.toLocaleString()}
          </div>
          <p className="text-gray-500 text-sm mt-4">
            {decision.earliest_date_for_full_payment ? `Full payment becomes safe on ${decision.earliest_date_for_full_payment}.` : 'Full payment is not safe within the forecast window.'}
          </p>
        </div>
        <div className="p-8 md:w-1/2 bg-gray-50 flex flex-col justify-center gap-6">
          <div>
            <div className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-1">Recommended Plan</div>
            <div className="text-lg font-medium text-gray-900 capitalize">
              {decision.recommended_payment_method ? decision.recommended_payment_method.replace('_', ' ') : 'None'}
            </div>
          </div>
          {decision.payment_plan && decision.payment_plan.length > 0 && (
            <div>
              <div className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-3">Timeline</div>
              <div className="flex flex-col gap-3 relative before:absolute before:inset-y-0 before:left-2 before:w-0.5 before:bg-gray-200 ml-1">
                {decision.payment_plan.map((p: any, i: number) => (
                  <div key={i} className="flex gap-4 relative z-10">
                    <div className="w-4 h-4 rounded-full bg-blue-500 border-4 border-gray-50 shrink-0 mt-0.5 -ml-1.5"></div>
                    <div>
                      <div className="text-sm font-semibold text-gray-900">₹{p.amount.toLocaleString()}</div>
                      <div className="text-xs text-gray-500">{p.date}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Explanation */}
      <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
        <div className="flex items-center gap-2 text-lg font-semibold text-gray-900 mb-4">
          <Info size={20} className="text-blue-500" />
          Why this decision?
        </div>
        <p className="text-gray-700 whitespace-pre-wrap text-sm leading-relaxed">
          {decision.decision_explanation}
        </p>
      </div>

      {/* Chart */}
      {chartData.length > 0 && (
        <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900 mb-6">90-Day Forecast</h2>
          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
                <XAxis dataKey="date" tick={{fontSize: 12, fill: '#6b7280'}} tickLine={false} axisLine={false} minTickGap={30} />
                <YAxis tick={{fontSize: 12, fill: '#6b7280'}} tickLine={false} axisLine={false} tickFormatter={(v) => `₹${v/1000}k`} />
                <Tooltip contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                <Line type="stepAfter" dataKey="balance" stroke="#2563eb" strokeWidth={2} dot={false} name="Projected Balance" />
                <Line type="stepAfter" dataKey="min" stroke="#dc2626" strokeWidth={1} strokeDasharray="5 5" dot={false} name="Minimum Required" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}
