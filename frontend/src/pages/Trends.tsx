import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { LineChart, BarChart3, Users, BookOpen, DollarSign } from 'lucide-react';

import { fetchTrendStats } from '@/services/statsService';

const Trends = () => {
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>(['visits', 'total_circulation']);
  const [selectedState, setSelectedState] = useState<string>('');
  
  const { data, isLoading, error } = useQuery({
    queryKey: ['trendStats', selectedMetrics, selectedState],
    queryFn: () => fetchTrendStats(selectedMetrics, undefined, undefined, selectedState || undefined),
    enabled: selectedMetrics.length > 0,
  });

  // Placeholder for state list
  const states = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'];
  
  // Available metrics
  const metrics = [
    { id: 'visits', name: 'Visits', icon: <Users className="h-5 w-5" /> },
    { id: 'total_circulation', name: 'Total Circulation', icon: <BookOpen className="h-5 w-5" /> },
    { id: 'electronic_circulation', name: 'E-Circulation', icon: <BookOpen className="h-5 w-5" /> },
    { id: 'physical_circulation', name: 'Physical Circulation', icon: <BookOpen className="h-5 w-5" /> },
    { id: 'total_programs', name: 'Programs', icon: <BarChart3 className="h-5 w-5" /> },
    { id: 'total_operating_revenue', name: 'Operating Revenue', icon: <DollarSign className="h-5 w-5" /> },
    { id: 'total_operating_expenditures', name: 'Operating Expenditures', icon: <DollarSign className="h-5 w-5" /> },
  ];

  const toggleMetric = (metricId: string) => {
    if (selectedMetrics.includes(metricId)) {
      setSelectedMetrics(selectedMetrics.filter(id => id !== metricId));
    } else {
      setSelectedMetrics([...selectedMetrics, metricId]);
    }
  };

  // Placeholder for chart - in a real implementation, we would use Chart.js or a similar library
  const renderChart = () => {
    if (!data) return null;
    
    return (
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="h-80 flex items-center justify-center border border-gray-200 rounded-lg">
          <div className="text-center">
            <LineChart className="h-12 w-12 text-primary-500 mx-auto mb-4" />
            <p className="text-gray-500">
              Chart would be rendered here with data for years: {data.years?.join(', ')}
            </p>
            <p className="text-gray-500 mt-2">
              Selected metrics: {selectedMetrics.join(', ')}
            </p>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Library Trends</h1>
      
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex flex-col md:flex-row gap-4 justify-between">
          <div>
            <h2 className="text-lg font-semibold mb-2">Select Metrics</h2>
            <div className="flex flex-wrap gap-2">
              {metrics.map(metric => (
                <button
                  key={metric.id}
                  onClick={() => toggleMetric(metric.id)}
                  className={`inline-flex items-center px-3 py-1 rounded-md ${
                    selectedMetrics.includes(metric.id)
                      ? 'bg-primary-100 text-primary-700 border border-primary-300'
                      : 'bg-gray-100 text-gray-700 border border-gray-200 hover:bg-gray-200'
                  }`}
                >
                  <span className="mr-1">{metric.icon}</span>
                  <span>{metric.name}</span>
                </button>
              ))}
            </div>
          </div>
          <div className="w-full md:w-48">
            <label htmlFor="state-select" className="block text-sm font-medium text-gray-700 mb-1">
              State
            </label>
            <select
              id="state-select"
              value={selectedState}
              onChange={(e) => setSelectedState(e.target.value)}
              className="block w-full rounded-md border-0 py-1.5 text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-primary-500 sm:text-sm"
            >
              <option value="">All States</option>
              {states.map(state => (
                <option key={state} value={state}>{state}</option>
              ))}
            </select>
          </div>
        </div>
      </div>
      
      {isLoading ? (
        <div className="animate-pulse">
          <div className="h-80 bg-gray-200 rounded-lg"></div>
        </div>
      ) : error ? (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          <p>Error loading trend data. Please try again later.</p>
        </div>
      ) : (
        <>
          {renderChart()}
          
          <div className="mt-6 bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4">About Library Trends</h2>
            <p className="text-gray-600 mb-4">
              This page allows you to visualize trends in library statistics over time. 
              Select one or more metrics to compare, and optionally filter by state.
            </p>
            <p className="text-gray-600">
              The data is sourced from the Public Libraries Survey (PLS) conducted annually 
              by the Institute of Museum and Library Services (IMLS).
            </p>
          </div>
        </>
      )}
    </div>
  );
};

export default Trends; 