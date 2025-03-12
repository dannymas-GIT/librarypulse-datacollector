// @ts-nocheck
import { Routes, Route, Navigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';

import Layout from '@/components/layout/Layout';
import Dashboard from '@/pages/Dashboard';
import Libraries from '@/pages/Libraries';
import LibraryDetails from '@/pages/LibraryDetails';
import Statistics from '@/pages/Statistics';
import Comparison from '@/pages/Comparison';
import DataManagement from '@/pages/DataManagement';
import NotFound from '@/pages/NotFound';
import HistoricalTrends from '@/pages/HistoricalTrends';
import SetupWizard from '@/pages/SetupWizard';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import libraryDataService from '@/services/libraryDataService';

function App() {
  const { data: setupComplete, isLoading } = useQuery({
    queryKey: ['setupStatus'],
    queryFn: libraryDataService.isSetupComplete
  });

  // Show loading spinner while checking setup status
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <Routes>
      {/* Setup wizard route */}
      <Route path="/setup" element={<SetupWizard />} />
      
      {/* Main application routes */}
      <Route 
        path="/" 
        element={setupComplete ? <Layout /> : <Navigate to="/setup" replace />}
      >
        <Route index element={<Dashboard />} />
        <Route path="libraries" element={<Libraries />} />
        <Route path="libraries/:libraryId" element={<LibraryDetails />} />
        <Route path="statistics" element={<Statistics />} />
        <Route path="historical" element={<HistoricalTrends />} />
        <Route path="comparison" element={<Comparison />} />
        <Route path="data-management" element={<DataManagement />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
}

export default App; 