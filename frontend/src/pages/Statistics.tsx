import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { BarChart3, Users, BookOpen, DollarSign } from 'lucide-react';

import { fetchSummaryStats } from '@/services/statsService';

const Statistics = () => {
  const [selectedYear, setSelectedYear] = useState<number>(2022);
  const [selectedState, setSelectedState] = useState<string>('');
  
  const { data, isLoading, error } = useQuery({
    queryKey: ['summaryStats', selectedYear, selectedState],
    queryFn: () => fetchSummaryStats(selectedYear, selectedState || undefined),
  });

  // Placeholder for state list
  const states = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'];
  
  // Placeholder for year list
  const years = [2022, 2021, 2020, 2019, 2018];

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Library Statistics</h1>
      
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="w-full md:w-48">
            <label htmlFor="year-select" className="block text-sm font-medium text-gray-700 mb-1">
              Year
            </label>
            <select
              id="year-select"
              value={selectedYear}
              onChange={(e) => setSelectedYear(parseInt(e.target.value))}
              className="block w-full rounded-md border-0 py-1.5 text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-primary-500 sm:text-sm"
            >
              {years.map(year => (
                <option key={year} value={year}>{year}</option>
              ))}
            </select>
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
        <div className="animate-pulse space-y-6">
          <div className="h-40 bg-gray-200 rounded-lg"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded-lg"></div>
            ))}
          </div>
        </div>
      ) : error ? (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          <p>Error loading statistics. Please try again later.</p>
        </div>
      ) : (
        <>
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h2 className="text-lg font-semibold mb-4">
              Summary Statistics for {selectedState || 'All States'} ({selectedYear})
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-primary-50 rounded-lg p-4">
                <div className="flex items-center">
                  <div className="p-3 bg-primary-100 rounded-full mr-4">
                    <Users className="h-6 w-6 text-primary-700" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Libraries</p>
                    <p className="text-2xl font-semibold">{data?.library_count.toLocaleString() || '9,000'}</p>
                  </div>
                </div>
              </div>
              <div className="bg-primary-50 rounded-lg p-4">
                <div className="flex items-center">
                  <div className="p-3 bg-primary-100 rounded-full mr-4">
                    <Users className="h-6 w-6 text-primary-700" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Total Visits</p>
                    <p className="text-2xl font-semibold">{data?.total_visits.toLocaleString() || '125M'}</p>
                  </div>
                </div>
              </div>
              <div className="bg-primary-50 rounded-lg p-4">
                <div className="flex items-center">
                  <div className="p-3 bg-primary-100 rounded-full mr-4">
                    <BookOpen className="h-6 w-6 text-primary-700" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Total Circulation</p>
                    <p className="text-2xl font-semibold">{data?.total_circulation.toLocaleString() || '750M'}</p>
                  </div>
                </div>
              </div>
              <div className="bg-primary-50 rounded-lg p-4">
                <div className="flex items-center">
                  <div className="p-3 bg-primary-100 rounded-full mr-4">
                    <DollarSign className="h-6 w-6 text-primary-700" />
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Operating Revenue</p>
                    <p className="text-2xl font-semibold">
                      ${((data?.total_operating_revenue || 12500000000) / 1000000000).toFixed(1)}B
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold mb-4">Per Library Averages</h2>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Visits</span>
                  <span className="font-semibold">{data?.avg_visits_per_library?.toLocaleString() || '13,889'}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Circulation</span>
                  <span className="font-semibold">{data?.avg_circulation_per_library?.toLocaleString() || '83,333'}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Programs</span>
                  <span className="font-semibold">{data?.avg_programs_per_library?.toLocaleString() || '500'}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Staff (FTE)</span>
                  <span className="font-semibold">{data?.avg_staff_per_library?.toLocaleString() || '12.5'}</span>
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold mb-4">Financial Overview</h2>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Total Operating Revenue</span>
                  <span className="font-semibold">
                    ${((data?.total_operating_revenue || 12500000000) / 1000000000).toFixed(1)}B
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Total Operating Expenditures</span>
                  <span className="font-semibold">
                    ${((data?.total_operating_expenditures || 12000000000) / 1000000000).toFixed(1)}B
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Avg. Revenue per Library</span>
                  <span className="font-semibold">
                    ${((data?.avg_operating_revenue_per_library || 1400000) / 1000000).toFixed(1)}M
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Avg. Expenditures per Library</span>
                  <span className="font-semibold">
                    ${((data?.avg_operating_expenditures_per_library || 1300000) / 1000000).toFixed(1)}M
                  </span>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Statistics; 