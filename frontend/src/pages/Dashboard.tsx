import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  BarChart3, 
  Users, 
  BookOpen, 
  Calendar, 
  TrendingUp, 
  TrendingDown, 
  Minus,
  Library,
  Clock
} from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Select } from '@/components/ui/Select';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { ErrorMessage } from '@/components/ui/ErrorMessage';
import { statsService } from '@/services/statsService';
import { libraryService } from '@/services/libraryService';

// Define types
interface KPI {
  name: string;
  value: number;
  previous_value?: number;
  change_percent?: number;
  trend?: string;
  unit?: string;
}

interface DashboardSummary {
  library_id: string;
  library_name: string;
  year: number;
  kpis: KPI[];
}

interface Library {
  id: string;
  name: string;
  location?: {
    city?: string;
    state?: string;
  };
}

// Helper function to format numbers
const formatNumber = (num: number): string => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M';
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K';
  } else {
    return num.toString();
  }
};

// Component for displaying a stat card
const StatCard: React.FC<{ kpi: any }> = ({ kpi }) => {
  // Determine icon based on metric name
  const getIcon = () => {
    switch (kpi.name) {
      case 'Total Circulation':
        return <BookOpen className="h-8 w-8 text-blue-500" />;
      case 'Visits':
        return <Users className="h-8 w-8 text-green-500" />;
      case 'Total Programs':
        return <Calendar className="h-8 w-8 text-purple-500" />;
      case 'Program Attendance':
        return <Users className="h-8 w-8 text-orange-500" />;
      case 'Reference Transactions':
        return <BarChart3 className="h-8 w-8 text-indigo-500" />;
      default:
        return <Library className="h-8 w-8 text-gray-500" />;
    }
  };

  // Determine trend icon and color
  const getTrendIcon = () => {
    if (!kpi.trend || !kpi.change_percent) return null;
    
    if (kpi.trend === 'up') {
      return <TrendingUp className="h-4 w-4 text-green-500" />;
    } else if (kpi.trend === 'down') {
      return <TrendingDown className="h-4 w-4 text-red-500" />;
    } else {
      return <Minus className="h-4 w-4 text-gray-500" />;
    }
  };

  return (
    <Card className="p-6">
      <div className="flex justify-between items-start">
        <div>
          <h3 className="text-lg font-medium text-gray-500">{kpi.name}</h3>
          <div className="mt-2 flex items-baseline">
            <p className="text-3xl font-semibold">{formatNumber(kpi.value)}</p>
            {kpi.unit && <span className="ml-1 text-sm text-gray-500">{kpi.unit}</span>}
          </div>
        </div>
        <div className="p-3 bg-blue-50 rounded-full">
          {getIcon()}
        </div>
      </div>
      {kpi.change_percent !== undefined && (
        <div className="mt-4 flex items-center text-sm">
          {getTrendIcon()}
          <span className={`ml-1 ${kpi.trend === 'up' ? 'text-green-600' : kpi.trend === 'down' ? 'text-red-600' : 'text-gray-600'}`}>
            {Math.abs(kpi.change_percent).toFixed(1)}% {kpi.trend === 'up' ? 'increase' : kpi.trend === 'down' ? 'decrease' : 'no change'}
          </span>
          <span className="ml-1 text-gray-500">from previous year</span>
        </div>
      )}
    </Card>
  );
};

const Dashboard: React.FC = () => {
  // State for selected library and year
  const [selectedLibrary, setSelectedLibrary] = useState<string>("NY0773"); // Default to West Babylon
  const [selectedYear, setSelectedYear] = useState<number>(2006); // Default year
  
  // Available years
  const years = Array.from({ length: 2022 - 2000 + 1 }, (_, i) => 2022 - i);
  
  // Fetch libraries
  const { data: libraries, isLoading: librariesLoading, error: librariesError } = useQuery({
    queryKey: ['libraries'],
    queryFn: async () => {
      const result = await libraryService.searchLibraries({ limit: 50 });
      return result.libraries;
    }
  });
  
  // Fetch dashboard data
  const { data: dashboardData, isLoading: dashboardLoading, error: dashboardError } = useQuery({
    queryKey: ['dashboard', selectedLibrary, selectedYear],
    queryFn: async () => {
      return statsService.getDashboardSummary(selectedLibrary, selectedYear);
    },
    enabled: !!selectedLibrary
  });
  
  // Handle loading states
  if (librariesLoading || dashboardLoading) {
    return (
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
        <div className="flex justify-center items-center h-64">
          <LoadingSpinner />
        </div>
      </div>
    );
  }
  
  // Handle error states
  if (librariesError || dashboardError) {
    return (
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
        <ErrorMessage message="Failed to load dashboard data. Please try again later." />
      </div>
    );
  }
  
  return (
    <div className="p-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
        <h1 className="text-2xl font-bold mb-4 md:mb-0">Dashboard</h1>
        
        <div className="flex flex-col sm:flex-row gap-4">
          {/* Library selector */}
          <div className="w-full sm:w-64">
            <Select
              label="Library"
              value={selectedLibrary}
              onChange={(e) => setSelectedLibrary(e.target.value)}
              options={libraries?.map(lib => ({
                value: lib.id,
                label: lib.name
              })) || []}
            />
          </div>
          
          {/* Year selector */}
          <div className="w-full sm:w-40">
            <Select
              label="Year"
              value={selectedYear.toString()}
              onChange={(e) => setSelectedYear(parseInt(e.target.value))}
              options={years.map(year => ({
                value: year.toString(),
                label: year.toString()
              }))}
            />
          </div>
        </div>
      </div>
      
      {dashboardData && (
        <>
          <div className="mb-6">
            <div className="bg-white rounded-lg shadow p-4 flex items-center">
              <Library className="h-6 w-6 text-blue-500 mr-3" />
              <div>
                <h2 className="text-xl font-semibold">{dashboardData.library_name}</h2>
                <p className="text-gray-500 text-sm flex items-center">
                  <Clock className="h-4 w-4 mr-1" />
                  Data for year {dashboardData.year}
                </p>
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {dashboardData.kpis.map((kpi, index) => (
              <StatCard key={index} kpi={kpi} />
            ))}
          </div>
        </>
      )}
    </div>
  );
};

export default Dashboard; 