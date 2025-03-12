import { Outlet } from 'react-router-dom';
import { BarChart, BookOpen, Library, FileText, Home, History, BarChart3 } from 'lucide-react';

import Navbar from './Navbar';
import Sidebar from './Sidebar';

const navItems = [
  { name: 'Dashboard', path: '/', icon: <Home className="w-5 h-5" /> },
  { name: 'Libraries', path: '/libraries', icon: <Library className="w-5 h-5" /> },
  { name: 'Historical Trends', path: '/historical', icon: <History className="w-5 h-5" /> },
  { name: 'Statistics', path: '/statistics', icon: <BarChart className="w-5 h-5" /> },
  { name: 'Comparison', path: '/comparison', icon: <BarChart3 className="w-5 h-5" /> },
  { name: 'Data Management', path: '/data-management', icon: <FileText className="w-5 h-5" /> },
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