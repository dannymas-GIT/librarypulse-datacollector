// @ts-nocheck
import { Routes, Route } from 'react-router-dom';

import Layout from '@/components/layout/Layout';
import Dashboard from '@/pages/Dashboard';
import Libraries from '@/pages/Libraries';
import LibraryDetails from '@/pages/LibraryDetails';
import Statistics from '@/pages/Statistics';
import Trends from '@/pages/Trends';
import Comparison from '@/pages/Comparison';
import DataManagement from '@/pages/DataManagement';
import NotFound from '@/pages/NotFound';
import HistoricalTrends from '@/pages/HistoricalTrends';
import ApiTest from '@/pages/ApiTest';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Dashboard />} />
        <Route path="libraries" element={<Libraries />} />
        <Route path="libraries/:libraryId" element={<LibraryDetails />} />
        <Route path="statistics" element={<Statistics />} />
        <Route path="trends" element={<Trends />} />
        <Route path="historical" element={<HistoricalTrends />} />
        <Route path="api-test" element={<ApiTest />} />
        <Route path="comparison" element={<Comparison />} />
        <Route path="data-management" element={<DataManagement />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
}

export default App; 