import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppShell } from './components/AppShell';
import { AuthProvider } from './context/AuthContext';
import Home from './pages/Home';
import Onboarding from './pages/Onboarding';
import Finances from './pages/Finances';
import Purchases from './pages/Purchases';
import RequestDetail from './pages/RequestDetail';
import NewRequest from './pages/NewRequest';
import Usage from './pages/Usage';
import DemoSelector from './pages/DemoSelector';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppShell>
          <Routes>
            <Route path="/" element={<Navigate to="/home" replace />} />
            <Route path="/home" element={<Home />} />
            <Route path="/onboarding" element={<Onboarding />} />
            <Route path="/finances" element={<Finances />} />
            <Route path="/purchases" element={<Purchases />} />
            <Route path="/purchases/new" element={<NewRequest />} />
            <Route path="/requests/:id" element={<RequestDetail />} />
            <Route path="/demo" element={<DemoSelector />} />
            <Route path="/system/usage" element={<Usage />} />
            {/* Fallbacks */}
            <Route path="/overview" element={<Navigate to="/home" replace />} />
            <Route path="/requests" element={<Navigate to="/purchases" replace />} />
          </Routes>
        </AppShell>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
