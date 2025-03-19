import { Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import Layout from '@/components/layout/Layout';
import Dashboard from '@/pages/Dashboard';
import Libraries from '@/pages/Libraries';
import LibraryDetails from '@/pages/LibraryDetails';
import Statistics from '@/pages/Statistics';
import Trends from '@/pages/Trends';
import Comparison from '@/pages/Comparison';
import DataManagement from '@/pages/DataManagement';
import NotFound from '@/pages/NotFound';
import SetupWizard from './components/setup/SetupWizard';
import SetupRequired from './components/routes/SetupRequired';
import AuthRequired from './components/routes/AuthRequired';
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import PasswordResetPage from './pages/PasswordResetPage';
import EmailVerificationPage from './pages/EmailVerificationPage';
import TermsPage from './pages/TermsPage';

// Create a client
const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Routes>
        {/* Public routes */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/forgot-password" element={<PasswordResetPage />} />
        <Route path="/verify-email/:token" element={<EmailVerificationPage />} />
        <Route path="/terms" element={<TermsPage />} />
        
        {/* Protected routes that require authentication */}
        <Route element={<AuthRequired />}>
          {/* Setup wizard route */}
          <Route path="/setup" element={<SetupWizard />} />
          
          {/* Protected routes that require setup */}
          <Route element={<SetupRequired />}>
            <Route path="/dashboard" element={<Layout />}>
              <Route index element={<Dashboard />} />
              <Route path="libraries" element={<Libraries />} />
              <Route path="libraries/:libraryId" element={<LibraryDetails />} />
              <Route path="statistics" element={<Statistics />} />
              <Route path="trends" element={<Trends />} />
              <Route path="comparison" element={<Comparison />} />
              <Route path="data-management" element={<DataManagement />} />
              <Route path="*" element={<NotFound />} />
            </Route>
          </Route>
        </Route>
      </Routes>
    </QueryClientProvider>
  );
}

export default App; 