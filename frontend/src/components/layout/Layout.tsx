import { Outlet } from 'react-router-dom';
import { BarChart4, BookOpen, LineChart, Library, FileDigit, Settings, Home, History, Wrench } from 'lucide-react';

import Navbar from './Navbar';
import Sidebar from './Sidebar';

const navItems = [
  { name: 'Dashboard', path: '/', icon: <Home className="w-5 h-5" /> },
  { name: 'Libraries', path: '/libraries', icon: <Library className="w-5 h-5" /> },
  { name: 'Statistics', path: '/statistics', icon: <BarChart4 className="w-5 h-5" /> },
  { name: 'Trends', path: '/trends', icon: <LineChart className="w-5 h-5" /> },
  { name: 'Historical', path: '/historical', icon: <History className="w-5 h-5" /> },
  { name: 'API Test', path: '/api-test', icon: <Wrench className="w-5 h-5" /> },
  { name: 'Comparison', path: '/comparison', icon: <BookOpen className="w-5 h-5" /> },
  { name: 'Data Management', path: '/data-management', icon: <FileDigit className="w-5 h-5" /> },
];

const Layout = () => {
  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar navItems={navItems} />
      <div className="flex flex-col flex-1 overflow-hidden">
        <Navbar />
        <div className="bg-blue-100 text-blue-800 px-4 py-2 text-sm">
          <strong>Using data for West Babylon Public Library.</strong> Historical data is loaded from backend API.
        </div>
        <main className="flex-1 overflow-y-auto p-4 md:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout; 