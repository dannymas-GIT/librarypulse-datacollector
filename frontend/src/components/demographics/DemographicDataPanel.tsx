import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { User, DollarSign, BookOpen, Home } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';

interface DemographicDataPanelProps {
  libraryId: string;
  year?: number;
}

export const DemographicDataPanel: React.FC<DemographicDataPanelProps> = ({ 
  libraryId,
  year 
}) => {
  // Fetch demographic data for the library
  const { data: demographicData, isLoading, error } = useQuery({
    queryKey: ['demographics', libraryId, year],
    queryFn: async () => {
      // For initial implementation, we're using the West Babylon endpoint
      // Later we will connect this to the library-specific endpoint
      const response = await fetch(`/demographics/west-babylon`);
      if (!response.ok) {
        throw new Error('Failed to fetch demographic data');
      }
      return response.json();
    },
    enabled: !!libraryId,
  });

  if (isLoading) {
    return (
      <Card className="p-6">
        <div>
          <h2 className="text-xl font-bold">Community Demographics</h2>
          <p className="text-gray-600">
            Loading demographic data for the library's service area...
          </p>
        </div>
        <div className="flex justify-center py-6">
          <LoadingSpinner />
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="p-6">
        <div>
          <h2 className="text-xl font-bold text-red-600">Error Loading Demographics</h2>
        </div>
        <div>
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded" role="alert">
            <p className="font-medium">Failed to load demographic data</p>
            <p className="text-sm">The demographic data service may be unavailable. Please try again later.</p>
          </div>
        </div>
      </Card>
    );
  }

  // If we have demographic data, display it
  if (demographicData) {
    return (
      <Card className="p-6">
        <div>
          <h2 className="text-xl font-bold">Community Demographics</h2>
          <p className="text-gray-600">
            {demographicData.geography?.name || 'Service Area'} Demographics
            {demographicData.source?.year && ` (${demographicData.source.year})`}
          </p>
        </div>
        <div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Population Statistics */}
            <div className="border rounded-lg p-4">
              <div className="flex items-center mb-3">
                <div className="p-2 bg-blue-100 rounded-full mr-3">
                  <User className="h-5 w-5 text-blue-700" />
                </div>
                <h3 className="text-lg font-medium">Population</h3>
              </div>
              <ul className="space-y-2">
                <li className="flex justify-between">
                  <span className="text-gray-600">Total Population</span>
                  <span className="font-medium">{demographicData.population?.total?.toLocaleString() || 'N/A'}</span>
                </li>
                <li className="flex justify-between">
                  <span className="text-gray-600">Median Age</span>
                  <span className="font-medium">{demographicData.population?.median_age || 'N/A'}</span>
                </li>
                <li className="flex justify-between">
                  <span className="text-gray-600">Under 18</span>
                  <span className="font-medium">
                    {demographicData.population?.by_age?.under_18?.toLocaleString() || '0'} 
                    {demographicData.population?.total && demographicData.population?.by_age?.under_18 && 
                      ` (${((demographicData.population.by_age.under_18 / demographicData.population.total) * 100).toFixed(1)}%)`}
                  </span>
                </li>
                <li className="flex justify-between">
                  <span className="text-gray-600">65 and Over</span>
                  <span className="font-medium">
                    {demographicData.population?.by_age?.over_65?.toLocaleString() || '0'} 
                    {demographicData.population?.total && demographicData.population?.by_age?.over_65 && 
                      ` (${((demographicData.population.by_age.over_65 / demographicData.population.total) * 100).toFixed(1)}%)`}
                  </span>
                </li>
              </ul>
            </div>

            {/* Economic Data */}
            <div className="border rounded-lg p-4">
              <div className="flex items-center mb-3">
                <div className="p-2 bg-green-100 rounded-full mr-3">
                  <DollarSign className="h-5 w-5 text-green-700" />
                </div>
                <h3 className="text-lg font-medium">Economics</h3>
              </div>
              <ul className="space-y-2">
                <li className="flex justify-between">
                  <span className="text-gray-600">Median Household Income</span>
                  <span className="font-medium">${demographicData.economics?.median_household_income?.toLocaleString() || 'N/A'}</span>
                </li>
                <li className="flex justify-between">
                  <span className="text-gray-600">Poverty Rate</span>
                  <span className="font-medium">{demographicData.economics?.poverty_rate}%</span>
                </li>
              </ul>
            </div>

            {/* Education Data */}
            <div className="border rounded-lg p-4">
              <div className="flex items-center mb-3">
                <div className="p-2 bg-purple-100 rounded-full mr-3">
                  <BookOpen className="h-5 w-5 text-purple-700" />
                </div>
                <h3 className="text-lg font-medium">Education</h3>
              </div>
              <ul className="space-y-2">
                <li className="flex justify-between">
                  <span className="text-gray-600">High School or Higher</span>
                  <span className="font-medium">{demographicData.education?.high_school_or_higher}%</span>
                </li>
                <li className="flex justify-between">
                  <span className="text-gray-600">Bachelor's Degree or Higher</span>
                  <span className="font-medium">{typeof demographicData.education?.bachelors_or_higher === 'number' ? 
                    demographicData.education.bachelors_or_higher.toFixed(1) : demographicData.education?.bachelors_or_higher}%</span>
                </li>
              </ul>
            </div>

            {/* Housing Data */}
            <div className="border rounded-lg p-4">
              <div className="flex items-center mb-3">
                <div className="p-2 bg-orange-100 rounded-full mr-3">
                  <Home className="h-5 w-5 text-orange-700" />
                </div>
                <h3 className="text-lg font-medium">Housing</h3>
              </div>
              <ul className="space-y-2">
                <li className="flex justify-between">
                  <span className="text-gray-600">Total Housing Units</span>
                  <span className="font-medium">{demographicData.housing?.total_units?.toLocaleString() || 'N/A'}</span>
                </li>
                <li className="flex justify-between">
                  <span className="text-gray-600">Owner-Occupied</span>
                  <span className="font-medium">
                    {demographicData.housing?.owner_occupied?.toLocaleString() || '0'} 
                    {demographicData.housing?.owner_occupied_percent && ` (${demographicData.housing.owner_occupied_percent}%)`}
                  </span>
                </li>
                <li className="flex justify-between">
                  <span className="text-gray-600">Median Home Value</span>
                  <span className="font-medium">${demographicData.housing?.median_home_value?.toLocaleString() || 'N/A'}</span>
                </li>
              </ul>
            </div>
          </div>

          {/* Data Source Information */}
          <div className="mt-6 pt-4 border-t text-xs text-gray-500">
            <p>
              Data Source: {demographicData.source?.name || 'American Community Survey'} 
              {demographicData.source?.year && ` (${demographicData.source.year})`}
            </p>
          </div>
        </div>
      </Card>
    );
  }

  // Fallback if no data is available
  return (
    <Card className="p-6">
      <div>
        <h2 className="text-xl font-bold">Community Demographics</h2>
        <p className="text-gray-600">
          Demographic data for the library's service area
        </p>
      </div>
      <div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="border rounded-lg p-4 flex flex-col items-center justify-center text-center space-y-2">
            <User className="h-12 w-12 text-blue-500" />
            <h3 className="text-lg font-medium">Population Data</h3>
            <p className="text-sm text-gray-500">
              Age distribution, race/ethnicity, and household information
            </p>
          </div>
          <div className="border rounded-lg p-4 flex flex-col items-center justify-center text-center space-y-2">
            <DollarSign className="h-12 w-12 text-green-500" />
            <h3 className="text-lg font-medium">Economic Data</h3>
            <p className="text-sm text-gray-500">
              Income levels, employment status, and poverty rates
            </p>
          </div>
          <div className="border rounded-lg p-4 flex flex-col items-center justify-center text-center space-y-2">
            <BookOpen className="h-12 w-12 text-purple-500" />
            <h3 className="text-lg font-medium">Education Data</h3>
            <p className="text-sm text-gray-500">
              Educational attainment and school enrollment
            </p>
          </div>
          <div className="border rounded-lg p-4 flex flex-col items-center justify-center text-center space-y-2">
            <Home className="h-12 w-12 text-orange-500" />
            <h3 className="text-lg font-medium">Housing Data</h3>
            <p className="text-sm text-gray-500">
              Housing units, occupancy, and property values
            </p>
          </div>
        </div>
      </div>
    </Card>
  );
};

export default DemographicDataPanel; 