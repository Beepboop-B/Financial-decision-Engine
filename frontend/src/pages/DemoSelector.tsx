import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function DemoSelector() {
  const navigate = useNavigate();
  const { login } = useAuth();
  
  const handleSelectDemo = (userId: string) => {
    login(userId);
    navigate('/home');
  };

  const handleCreateNew = () => {
    navigate('/onboarding');
  };

  return (
    <div className="flex flex-col gap-8 max-w-3xl mx-auto mt-12">
      <div className="text-center">
        <h1 className="text-3xl font-semibold text-gray-900 tracking-tight mb-3">Welcome to Buy or Wait</h1>
        <p className="text-gray-500">Know what you can safely afford before you buy.</p>
      </div>

      <div className="grid md:grid-cols-2 gap-6 mt-8">
        
        {/* New User Path */}
        <div className="bg-white border border-gray-200 rounded-2xl p-8 shadow-sm flex flex-col gap-6">
          <div>
            <div className="w-12 h-12 bg-blue-100 text-blue-600 rounded-xl flex items-center justify-center font-bold text-xl mb-4">
              +
            </div>
            <h2 className="text-xl font-semibold text-gray-900">Personal Account</h2>
            <p className="text-sm text-gray-500 mt-2 leading-relaxed">
              Create your own financial profile. Enter your balances and recurring expenses to see if you can afford a real purchase.
            </p>
          </div>
          <button 
            onClick={handleCreateNew}
            className="mt-auto w-full py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
          >
            Create Profile &rarr;
          </button>
        </div>

        {/* Demo Path */}
        <div className="bg-gray-50 border border-gray-200 rounded-2xl p-8 shadow-sm flex flex-col gap-6">
          <div>
            <div className="w-12 h-12 bg-gray-200 text-gray-600 rounded-xl flex items-center justify-center font-bold text-xl mb-4">
              D
            </div>
            <h2 className="text-xl font-semibold text-gray-900">Demo Dataset</h2>
            <p className="text-sm text-gray-500 mt-2 leading-relaxed">
              Explore the system using pre-loaded anonymous challenge data. Contains hundreds of test scenarios.
            </p>
          </div>
          
          <div className="mt-auto flex flex-col gap-2">
            <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Select a demo user:</span>
            <button 
              onClick={() => handleSelectDemo('user_26')}
              className="w-full py-2 bg-white border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
            >
              Load User 26 (Affordable Plan)
            </button>
            <button 
              onClick={() => handleSelectDemo('user_01')}
              className="w-full py-2 bg-white border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
            >
              Load User 01 (Not Affordable)
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}
