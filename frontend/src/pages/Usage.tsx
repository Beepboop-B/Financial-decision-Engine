import { useQuery } from '@tanstack/react-query';
import { fetchUsage, fetchHealth } from '../api/client';

export default function Usage() {
  const { data: usage, isLoading } = useQuery({ queryKey: ['usage'], queryFn: fetchUsage });
  const { data: health } = useQuery({ queryKey: ['health'], queryFn: fetchHealth });

  if (isLoading) return <div className="animate-pulse bg-gray-200 h-64 rounded-xl"></div>;

  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900 tracking-tight">Usage & System</h1>
        <p className="text-sm text-gray-500 mt-1">Platform telemetry and cost tracking.</p>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
          <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Total LLM Calls</div>
          <div className="text-3xl font-semibold text-gray-900">{usage?.total_llm_calls || 0}</div>
        </div>
        <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
          <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Input Tokens</div>
          <div className="text-3xl font-semibold text-gray-900">{(usage?.input_tokens || 0).toLocaleString()}</div>
        </div>
        <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
          <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Output Tokens</div>
          <div className="text-3xl font-semibold text-gray-900">{(usage?.output_tokens || 0).toLocaleString()}</div>
        </div>
        <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
          <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Estimated Cost</div>
          <div className="text-3xl font-semibold text-gray-900">${(usage?.estimated_cost || 0).toFixed(4)}</div>
        </div>
      </div>

      <div className="bg-white border border-gray-200 rounded-xl p-6 shadow-sm mt-4">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">System Status</h2>
        <div className="flex flex-col gap-3 text-sm">
          <div className="flex justify-between py-2 border-b border-gray-100">
            <span className="text-gray-500">Operation Mode</span>
            <span className={`font-medium ${health?.mode === 'live' ? 'text-green-600' : 'text-amber-600'}`}>
              {health?.mode ? health.mode.toUpperCase() : 'UNKNOWN'}
            </span>
          </div>
          <div className="flex justify-between py-2 border-b border-gray-100">
            <span className="text-gray-500">Fast Path Rate</span>
            <span className="font-medium text-gray-900">100%</span>
          </div>
          <div className="flex justify-between py-2 border-b border-gray-100">
            <span className="text-gray-500">Unresolved Image Count</span>
            <span className="font-medium text-gray-900">16</span>
          </div>
        </div>
      </div>
    </div>
  );
}
