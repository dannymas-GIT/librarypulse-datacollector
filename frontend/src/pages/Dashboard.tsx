import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Select } from '@/components/ui/Select';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { ErrorMessage } from '@/components/ui/ErrorMessage';
import { Card } from '@/components/ui/Card';
import statsService from '@/services/statsService';
import { libraryService } from '@/services/libraryService';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

// Define types for KPI and DashboardSummary since they're not exported from statsService
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

// Simple stat card component
const StatCard: React.FC<{ kpi: KPI }> = ({ kpi }) => {
  const trendText = kpi.trend === 'up' 
    ? 'Increased' 
    : kpi.trend === 'down' 
      ? 'Decreased' 
      : 'No change';
  
  const trendClass = kpi.trend === 'up' 
    ? 'text-green-600' 
    : kpi.trend === 'down' 
      ? 'text-red-600' 
      : 'text-gray-600';

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-medium text-gray-500">{kpi.name}</h3>
      <p className="text-3xl font-semibold mt-2">
        {formatNumber(kpi.value)}
        {kpi.unit && <span className="ml-1 text-sm text-gray-500">{kpi.unit}</span>}
      </p>
      {kpi.change_percent !== undefined && (
        <p className={`mt-2 text-sm ${trendClass}`}>
          {trendText} by {Math.abs(kpi.change_percent).toFixed(1)}% from previous year
        </p>
      )}
    </div>
  );
};

// Chart component for visualizing KPI data
const KpiChart: React.FC<{ kpis: KPI[] }> = ({ kpis }) => {
  // Prepare data for the chart
  const chartData = kpis.map(kpi => ({
    name: kpi.name,
    current: kpi.value,
    previous: kpi.previous_value || 0
  }));

  return (
    <Card className="p-6 mt-6">
      <h2 className="text-xl font-semibold mb-4">Key Metrics Comparison</h2>
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            margin={{ top: 20, right: 30, left: 20, bottom: 70 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="name" 
              angle={-45} 
              textAnchor="end"
              height={70}
              interval={0}
            />
            <YAxis />
            <Tooltip formatter={(value) => formatNumber(value as number)} />
            <Legend />
            <Bar dataKey="current" name="Current Year" fill="#8884d8" />
            <Bar dataKey="previous" name="Previous Year" fill="#82ca9d" />
          </BarChart>
        </ResponsiveContainer>
      </div>
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
      return statsService.getDashboardSummary(selectedLibrary, selectedYear) as Promise<DashboardSummary>;
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
  
  // Handle Select onChange events
  const handleLibraryChange = (value: string) => {
    setSelectedLibrary(value);
  };
  
  const handleYearChange = (value: string) => {
    setSelectedYear(parseInt(value));
  };
  
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
              onChange={handleLibraryChange}
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
              onChange={handleYearChange}
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
            <div className="bg-white rounded-lg shadow p-4">
              <h2 className="text-xl font-semibold">{dashboardData.library_name}</h2>
              <p className="text-gray-500 text-sm">
                Data for year {dashboardData.year}
              </p>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {dashboardData.kpis.map((kpi, index) => (
              <StatCard key={index} kpi={kpi} />
            ))}
          </div>
          
          {/* Add chart visualization */}
          <KpiChart kpis={dashboardData.kpis} />
          
          {/* Additional metrics section */}
          <Card className="p-6 mt-6">
            <h2 className="text-xl font-semibold mb-4">Additional Library Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-medium text-gray-700 mb-2">Collection Overview</h3>
                <ul className="space-y-2">
                  {dashboardData.kpis
                    .filter(kpi => kpi.name.includes('Collection'))
                    .map((kpi, index) => (
                      <li key={index} className="flex justify-between">
                        <span className="text-gray-600">{kpi.name}</span>
                        <span className="font-medium">{formatNumber(kpi.value)}</span>
                      </li>
                    ))}
                </ul>
              </div>
              <div>
                <h3 className="text-lg font-medium text-gray-700 mb-2">Program Statistics</h3>
                <ul className="space-y-2">
                  {dashboardData.kpis
                    .filter(kpi => kpi.name.includes('Program'))
                    .map((kpi, index) => (
                      <li key={index} className="flex justify-between">
                        <span className="text-gray-600">{kpi.name}</span>
                        <span className="font-medium">{formatNumber(kpi.value)}</span>
                      </li>
                    ))}
                </ul>
              </div>
            </div>
          </Card>
        </>
      )}
    </div>
  );
};

export default Dashboard; 