import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { onboardUser } from '../api/client';
import { Plus } from 'lucide-react';

export default function Onboarding() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);

  const [formData, setFormData] = useState({
    user_id: `user_new_${Math.random().toString(36).substr(2, 6)}`,
    current_balance: '',
    minimum_balance: '',
    home_currency: 'INR',
    income: [{ source: 'Salary', amount: '', frequency: 'monthly' }],
    recurring_expenses: [] as any[],
    obligations: [] as any[],
    payment_preferences: {
      full_payment: true,
      partial_payment: true,
      installments: true
    }
  });

  const addExpense = () => setFormData({...formData, recurring_expenses: [...formData.recurring_expenses, { name: '', amount: '' }]});
  
  
  const updateExpense = (idx: number, field: string, val: string) => {
    const arr = [...formData.recurring_expenses];
    arr[idx] = { ...arr[idx], [field]: val };
    setFormData({...formData, recurring_expenses: arr});
  };

  const submitProfile = async () => {
    setLoading(true);
    try {
      const prefs = Object.entries(formData.payment_preferences)
        .filter(([_, checked]) => checked)
        .map(([method]) => method);

      const payload = {
        ...formData,
        current_balance: parseFloat(formData.current_balance || '0'),
        minimum_balance: parseFloat(formData.minimum_balance || '0'),
        payment_preferences: prefs,
        income: formData.income.map(i => ({...i, amount: parseFloat(i.amount || '0')})),
        recurring_expenses: formData.recurring_expenses.map(e => ({...e, amount: parseFloat(e.amount || '0')})),
        obligations: formData.obligations.map(o => ({...o, amount: parseFloat(o.amount || '0')})),
      };

      const res = await onboardUser(payload);
      login(res.user_id);
      navigate('/home');
    } catch (err) {
      console.error(err);
      setLoading(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto mt-8 bg-white border border-gray-200 shadow-sm rounded-2xl p-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8 pb-6 border-b border-gray-100">
        <div>
          <h1 className="text-xl font-semibold text-gray-900 tracking-tight">Set up your profile</h1>
          <p className="text-sm text-gray-500 mt-1">Step {step} of 4</p>
        </div>
        <div className="flex gap-2">
          {[1,2,3,4].map(s => (
            <div key={s} className={`w-2 h-2 rounded-full ${s <= step ? 'bg-blue-600' : 'bg-gray-200'}`} />
          ))}
        </div>
      </div>

      {step === 1 && (
        <div className="flex flex-col gap-6">
          <h2 className="text-lg font-medium text-gray-900">Let's start with your balance</h2>
          <div className="flex flex-col gap-4">
            <div>
              <label className="text-sm font-semibold text-gray-900 block mb-2">Home Currency</label>
              <select 
                value={formData.home_currency}
                onChange={(e) => setFormData({...formData, home_currency: e.target.value})}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-blue-500"
              >
                <option value="INR">INR</option>
                <option value="USD">USD</option>
                <option value="EUR">EUR</option>
              </select>
            </div>
            <div>
              <label className="text-sm font-semibold text-gray-900 block mb-2">Current Balance</label>
              <input type="number" placeholder="e.g. 100000" required value={formData.current_balance} onChange={(e) => setFormData({...formData, current_balance: e.target.value})} className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-blue-500" />
            </div>
            <div>
              <label className="text-sm font-semibold text-gray-900 block mb-2">Minimum Safe Buffer</label>
              <p className="text-xs text-gray-500 mb-2">Amount you never want to drop below.</p>
              <input type="number" placeholder="e.g. 20000" required value={formData.minimum_balance} onChange={(e) => setFormData({...formData, minimum_balance: e.target.value})} className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-blue-500" />
            </div>
          </div>
          <button onClick={() => setStep(2)} disabled={!formData.current_balance} className="mt-4 bg-blue-600 text-white py-2.5 rounded-lg font-medium">Next &rarr;</button>
        </div>
      )}

      {step === 2 && (
        <div className="flex flex-col gap-6">
          <h2 className="text-lg font-medium text-gray-900">Monthly Income</h2>
          <div className="flex flex-col gap-4">
            <div>
              <label className="text-sm font-semibold text-gray-900 block mb-2">Amount</label>
              <input type="number" placeholder="e.g. 75000" value={formData.income[0].amount} onChange={(e) => setFormData({...formData, income: [{...formData.income[0], amount: e.target.value}]})} className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-blue-500" />
            </div>
          </div>
          <div className="flex gap-4 mt-4">
            <button onClick={() => setStep(1)} className="px-6 py-2.5 border border-gray-300 rounded-lg font-medium text-gray-700">Back</button>
            <button onClick={() => setStep(3)} className="flex-1 bg-blue-600 text-white py-2.5 rounded-lg font-medium">Next &rarr;</button>
          </div>
        </div>
      )}

      {step === 3 && (
        <div className="flex flex-col gap-6">
          <h2 className="text-lg font-medium text-gray-900">Recurring Expenses</h2>
          <p className="text-sm text-gray-500">Rent, utilities, subscriptions.</p>
          
          <div className="flex flex-col gap-4">
            {formData.recurring_expenses.map((exp: any, i: number) => (
              <div key={i} className="flex gap-4 items-center">
                <input type="text" placeholder="Name" value={exp.name} onChange={(e) => updateExpense(i, 'name', e.target.value)} className="flex-1 px-4 py-2 border border-gray-300 rounded-lg" />
                <input type="number" placeholder="Amount" value={exp.amount} onChange={(e) => updateExpense(i, 'amount', e.target.value)} className="w-32 px-4 py-2 border border-gray-300 rounded-lg" />
              </div>
            ))}
            <button onClick={addExpense} className="flex items-center gap-2 text-sm text-blue-600 font-medium py-2"><Plus size={16}/> Add Expense</button>
          </div>
          <div className="flex gap-4 mt-4">
            <button onClick={() => setStep(2)} className="px-6 py-2.5 border border-gray-300 rounded-lg font-medium text-gray-700">Back</button>
            <button onClick={() => setStep(4)} className="flex-1 bg-blue-600 text-white py-2.5 rounded-lg font-medium">Next &rarr;</button>
          </div>
        </div>
      )}

      {step === 4 && (
        <div className="flex flex-col gap-6">
          <h2 className="text-lg font-medium text-gray-900">Payment Preferences</h2>
          <p className="text-sm text-gray-500">How are you willing to pay for things?</p>
          
          <div className="flex flex-col gap-3">
            <label className="flex items-center gap-3"><input type="checkbox" checked={formData.payment_preferences.full_payment} readOnly className="w-4 h-4 text-blue-600 rounded" /><span className="text-sm font-medium">Full Payment</span></label>
            <label className="flex items-center gap-3"><input type="checkbox" checked={formData.payment_preferences.partial_payment} onChange={(e) => setFormData({...formData, payment_preferences: {...formData.payment_preferences, partial_payment: e.target.checked}})} className="w-4 h-4 text-blue-600 rounded" /><span className="text-sm font-medium">Partial Payment</span></label>
            <label className="flex items-center gap-3"><input type="checkbox" checked={formData.payment_preferences.installments} onChange={(e) => setFormData({...formData, payment_preferences: {...formData.payment_preferences, installments: e.target.checked}})} className="w-4 h-4 text-blue-600 rounded" /><span className="text-sm font-medium">Installments</span></label>
          </div>

          <div className="flex gap-4 mt-8">
            <button onClick={() => setStep(3)} className="px-6 py-2.5 border border-gray-300 rounded-lg font-medium text-gray-700">Back</button>
            <button onClick={submitProfile} disabled={loading} className="flex-1 bg-blue-600 text-white py-2.5 rounded-lg font-medium">
              {loading ? 'Saving...' : 'Finish Setup'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
