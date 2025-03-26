import React, { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  BarChart3,
  BookOpen,
  Users,
  Clock,
  Calendar,
  DollarSign,
  Layers,
  Globe,
  FileBox,
  Loader2,
  AlertCircle,
} from 'lucide-react';
import { Link } from 'react-router-dom';

import { libraryConfigService } from '../services/libraryConfigService';
import { API_BASE_URL } from '../config';

interface StatCard {
  title: string;
  value: string | number;
  change: string;
  icon: React.ReactNode;
  isPositive: boolean;
  isNegative?: boolean;
}

interface LibraryStats {
  name: string;
  city: string;
  state: string;
  recent_data: {
    year: number;
    visits: number;
    circulation: {
      total: number;
      electronic: number;
      physical: number;
    };
    collections: {
      print: number;
      electronic: number;
      audio: number;
      video: number;
    };
    programs: {
      total: number;
      attendance: number;
    };
    revenue: number;
    expenditures: number;
    staff: number;
  };
  trends: {
    visits: Array<{ year: number; value: number }>;
    circulation: Array<{ year: number; value: number }>;
    programs: Array<{ year: number; value: number }>;
    revenue: Array<{ year: number; value: number }>;
  };
}

const StatCard = ({ title, value, icon, description, color }: {
  title: string;
  value: string | number;
  icon: React.ReactNode;
  description?: string;
  color: string;
}) => (
  <div className="bg-white rounded-lg shadow p-6">
    <div className="flex items-center">
      <div className={`p-3 rounded-full ${color} text-white mr-4`}>
        {icon}
      </div>
      <div>
        <p className="text-sm font-medium text-gray-500">{title}</p>
        <p className="text-2xl font-semibold">{value}</p>
        {description && <p className="text-xs text-gray-500 mt-1">{description}</p>}
      </div>
    </div>
  </div>
);

const Dashboard: React.FC = () => {
  const [libraryStats, setLibraryStats] = useState<LibraryStats | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Get the library configuration
  const {
    data: config,
    isLoading: configLoading,
    error: configError
  } = useQuery({
    queryKey: ['libraryConfig'],
    queryFn: () => libraryConfigService.getConfig(),
  });

  // Get the library statistics (using the library_id from config)
  const {
    data: stats,
    isLoading: statsLoading,
    error: statsError
  } = useQuery({
    queryKey: ['libraryStats', config?.library_id],
    queryFn: async () => {
      if (!config?.library_id) return null;
      const response = await fetch(`${API_BASE_URL}/stats/library/${config.library_id}/dashboard`);
      if (!response.ok) {
        throw new Error('Failed to fetch library statistics');
      }
      return response.json();
    },
    enabled: !!config?.library_id,
  });

  useEffect(() => {
    if (stats) {
      setLibraryStats(stats);
    }
    
    if (statsError) {
      setError('Failed to load library statistics');
    } else if (configError) {
      setError('Failed to load library configuration');
    }
  }, [stats, statsError, configError]);

  // Generate statistic cards
  const generateStatCards = (): StatCard[] => {
    if (!libraryStats) return [];

    return [
      {
        title: 'Total Visits',
        value: libraryStats.recent_data.visits.toLocaleString(),
        change: '+5.2%',
        icon: <Users className="w-8 h-8 text-blue-500" />,
        isPositive: true,
      },
      {
        title: 'Total Circulation',
        value: libraryStats.recent_data.circulation.total.toLocaleString(),
        change: '+3.8%',
        icon: <BookOpen className="w-8 h-8 text-emerald-500" />,
        isPositive: true,
      },
      {
        title: 'Electronic Circulation',
        value: libraryStats.recent_data.circulation.electronic.toLocaleString(),
        change: '+12.5%',
        icon: <Globe className="w-8 h-8 text-purple-500" />,
        isPositive: true,
      },
      {
        title: 'Programs Held',
        value: libraryStats.recent_data.programs.total.toLocaleString(),
        change: '+7.3%',
        icon: <Calendar className="w-8 h-8 text-indigo-500" />,
        isPositive: true,
      },
      {
        title: 'Program Attendance',
        value: libraryStats.recent_data.programs.attendance.toLocaleString(),
        change: '+8.1%',
        icon: <Users className="w-8 h-8 text-rose-500" />,
        isPositive: true,
      },
      {
        title: 'Operating Revenue',
        value: `$${(libraryStats.recent_data.revenue / 1000).toLocaleString()}K`,
        change: '+2.4%',
        icon: <DollarSign className="w-8 h-8 text-green-500" />,
        isPositive: true,
      },
      {
        title: 'Operating Expenditures',
        value: `$${(libraryStats.recent_data.expenditures / 1000).toLocaleString()}K`,
        change: '+3.1%',
        icon: <DollarSign className="w-8 h-8 text-amber-500" />,
        isPositive: true,
      },
      {
        title: 'Staff (FTE)',
        value: libraryStats.recent_data.staff.toLocaleString(),
        change: '-1.2%',
        icon: <Users className="w-8 h-8 text-cyan-500" />,
        isPositive: false,
        isNegative: true,
      },
    ];
  };

  if (configLoading || statsLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[calc(100vh-6rem)]">
        <Loader2 className="w-12 h-12 text-blue-500 animate-spin mb-4" />
        <h2 className="text-lg font-medium text-gray-600">Loading library data...</h2>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[calc(100vh-6rem)]">
        <AlertCircle className="w-12 h-12 text-red-500 mb-4" />
        <h2 className="text-lg font-medium text-gray-800">{error}</h2>
        <p className="text-gray-600 mt-2">
          Please check your configuration or try again later.
        </p>
      </div>
    );
  }

  if (!config || !libraryStats) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[calc(100vh-6rem)]">
        <FileBox className="w-12 h-12 text-amber-500 mb-4" />
        <h2 className="text-lg font-medium text-gray-800">No library data available</h2>
        <p className="text-gray-600 mt-2">
          Please complete the setup wizard to configure your library.
        </p>
      </div>
    );
  }

  const statCards = generateStatCards();

  return (
    <div className="p-6">
      {/* Library Header */}
      <div className="bg-white p-6 rounded-lg shadow-md mb-6">
        <h1 className="text-3xl font-bold text-gray-800">{libraryStats.name}</h1>
        <p className="text-gray-600">
          {libraryStats.city}, {libraryStats.state} | Data for FY {libraryStats.recent_data.year}
        </p>
        <div className="mt-4 flex flex-wrap gap-4">
          <div className="flex items-center">
            <Clock className="w-5 h-5 text-blue-500 mr-2" />
            <span>Most Recent Data: FY {libraryStats.recent_data.year}</span>
          </div>
          <div className="flex items-center">
            <Layers className="w-5 h-5 text-emerald-500 mr-2" />
            <span>Data Years Available: {libraryStats.trends.visits.length}</span>
          </div>
        </div>
      </div>

      {/* Stat Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        {statCards.map((stat, index) => (
          <div key={index} className="bg-white p-6 rounded-lg shadow-md">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="text-gray-500 font-medium">{stat.title}</h3>
                <p className="text-2xl font-bold mt-1">{stat.value}</p>
              </div>
              <div className="p-2 rounded-md bg-gray-50">{stat.icon}</div>
            </div>
            <div className="mt-2">
              <span
                className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  stat.isPositive
                    ? 'bg-green-100 text-green-800'
                    : stat.isNegative
                    ? 'bg-red-100 text-red-800'
                    : 'bg-yellow-100 text-yellow-800'
                }`}
              >
                {stat.change}
              </span>
              <span className="text-gray-500 text-xs ml-1">from previous year</span>
            </div>
          </div>
        ))}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <Users className="w-5 h-5 text-blue-500 mr-2" />
            Yearly Visits
          </h2>
          <div className="h-80 flex items-center justify-center bg-gray-50 rounded-md">
            <BarChart3 className="w-16 h-16 text-gray-300" />
            <span className="ml-2 text-gray-500">Visit trend chart goes here</span>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4 flex items-center">
            <BookOpen className="w-5 h-5 text-emerald-500 mr-2" />
            Circulation Trends
          </h2>
          <div className="h-80 flex items-center justify-center bg-gray-50 rounded-md">
            <BarChart3 className="w-16 h-16 text-gray-300" />
            <span className="ml-2 text-gray-500">Circulation trend chart goes here</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Link
              to="/libraries"
              className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors"
            >
              <Library className="h-5 w-5 text-primary-600 mr-3" />
              <span>Browse Libraries</span>
            </Link>
            <Link
              to="/trends"
              className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors"
            >
              <TrendingUp className="h-5 w-5 text-primary-600 mr-3" />
              <span>View Trends</span>
            </Link>
            <Link
              to="/statistics"
              className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors"
            >
              <BarChart3 className="h-5 w-5 text-primary-600 mr-3" />
              <span>Statistics</span>
            </Link>
            <Link
              to="/data-management"
              className="flex items-center p-4 border rounded-lg hover:bg-gray-50 transition-colors"
            >
              <BookOpen className="h-5 w-5 text-primary-600 mr-3" />
              <span>Data Management</span>
            </Link>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">About Library Lens</h2>
          <p className="text-gray-600 mb-4">
            Library Lens provides analytics and insights based on the Public Libraries Survey (PLS) 
            data collected annually by the Institute of Museum and Library Services (IMLS).
          </p>
          <p className="text-gray-600">
            Use this tool to explore library statistics, compare libraries, analyze trends, 
            and make data-driven decisions for your library.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 