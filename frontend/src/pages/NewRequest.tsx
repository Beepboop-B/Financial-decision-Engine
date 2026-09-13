import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { createRequest } from '../api/client';
import { ShoppingCart } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export default function NewRequest() {
  const navigate = useNavigate();
  const { userId } = useAuth();
  const [loading, setLoading] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState('');
  
  const [formData, setFormData] = useState({
    user_id: userId || '',
    request_text: '',
    requested_amount: '',
    currency: 'INR',
    desired_completion_date: '',
    request_type: 'purchase',
    allows_partial_payment: false,
    methods: {
      full_payment: true,
      partial_payment: false,
      installments: false
    }
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setLoadingMessage('Reconstructing financial state...');

    const payment_methods = Object.entries(formData.methods)
      .filter(([_, checked]) => checked)
      .map(([method]) => method);

    try {
      setTimeout(() => setLoadingMessage('Checking 90-day cash flow...'), 800);
      setTimeout(() => setLoadingMessage('Comparing payment plans...'), 1600);

      const res = await createRequest({
        user_id: formData.user_id,
        request_text: formData.request_text,
        requested_amount: parseFloat(formData.requested_amount),
        currency: formData.currency,
        desired_completion_date: formData.desired_completion_date,
        request_type: formData.request_type,
        allows_partial_payment: formData.allows_partial_payment,
        payment_methods
      });

      setTimeout(() => {
        navigate(`/requests/${res.request_id}`);
      }, 2400);
    } catch (err) {
      console.error(err);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-96 gap-4">
        <div className="w-12 h-12 rounded-full border-4 border-blue-100 border-t-blue-600 animate-spin"></div>
        <div className="text-gray-600 font-medium">{loadingMessage}</div>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="flex items-center gap-3 mb-8">
        <div className="p-3 bg-blue-100 text-blue-600 rounded-xl">
          <ShoppingCart size={24} />
        </div>
        <div>
          <h1 className="text-2xl font-semibold text-gray-900 tracking-tight">New Purchase Request</h1>
          <p className="text-sm text-gray-500 mt-1">Evaluate affordability against your 90-day cash flow.</p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="bg-white border border-gray-200 shadow-sm rounded-2xl p-8 flex flex-col gap-8">
        
        <div className="flex flex-col gap-2">
          <label className="text-sm font-semibold text-gray-900">What are you buying?</label>
          <input 
            required 
            type="text" 
            placeholder="e.g., MacBook Pro"
            value={formData.request_text}
            onChange={(e) => setFormData({...formData, request_text: e.target.value})}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
          />
        </div>

        <div className="grid grid-cols-2 gap-6">
          <div className="flex flex-col gap-2">
            <label className="text-sm font-semibold text-gray-900">Requested Amount</label>
            <div className="relative flex">
              <select 
                value={formData.currency}
                onChange={(e) => setFormData({...formData, currency: e.target.value})}
                className="pl-3 pr-8 py-2 border border-gray-300 rounded-l-lg bg-gray-50 text-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="INR">INR</option>
                <option value="USD">USD</option>
                <option value="EUR">EUR</option>
              </select>
              <input 
                required 
                type="number" 
                min="1"
                placeholder="60000"
                value={formData.requested_amount}
                onChange={(e) => setFormData({...formData, requested_amount: e.target.value})}
                className="w-full px-4 py-2 border border-l-0 border-gray-300 rounded-r-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
              />
            </div>
          </div>
          <div className="flex flex-col gap-2">
            <label className="text-sm font-semibold text-gray-900">Deadline</label>
            <input 
              required 
              type="date"
              value={formData.desired_completion_date}
              onChange={(e) => setFormData({...formData, desired_completion_date: e.target.value})}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
            />
          </div>
        </div>
        
        <div className="flex flex-col gap-2">
          <label className="text-sm font-semibold text-gray-900">Request Type</label>
          <select
            value={formData.request_type}
            onChange={(e) => setFormData({...formData, request_type: e.target.value})}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
          >
            <option value="purchase">Purchase</option>
            <option value="travel">Travel</option>
            <option value="investment">Investment</option>
          </select>
        </div>

        <div className="flex flex-col gap-3">
          <label className="text-sm font-semibold text-gray-900">Payment Options</label>
          <div className="flex flex-col gap-3">
            <label className="flex items-center gap-3">
              <input 
                type="checkbox" 
                checked={formData.methods.full_payment}
                onChange={(e) => setFormData({...formData, methods: {...formData.methods, full_payment: e.target.checked}})}
                className="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500" 
              />
              <span className="text-sm text-gray-700">Full Payment</span>
            </label>
            <label className="flex items-center gap-3">
              <input 
                type="checkbox" 
                checked={formData.methods.partial_payment}
                onChange={(e) => {
                  setFormData({
                    ...formData, 
                    methods: {...formData.methods, partial_payment: e.target.checked},
                    allows_partial_payment: e.target.checked
                  })
                }}
                className="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500" 
              />
              <span className="text-sm text-gray-700">Partial Payment</span>
            </label>
            <label className="flex items-center gap-3">
              <input 
                type="checkbox" 
                checked={formData.methods.installments}
                onChange={(e) => setFormData({...formData, methods: {...formData.methods, installments: e.target.checked}})}
                className="w-4 h-4 text-blue-600 rounded border-gray-300 focus:ring-blue-500" 
              />
              <span className="text-sm text-gray-700">Installments</span>
            </label>
          </div>
        </div>

        <div className="pt-4 border-t border-gray-100 flex justify-end">
          <button 
            type="submit" 
            disabled={!Object.values(formData.methods).some(v => v)}
            className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-6 py-2.5 rounded-lg font-medium transition-colors"
          >
            Evaluate affordability &rarr;
          </button>
        </div>
      </form>
    </div>
  );
}
