import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { ErrorMessage } from '@/components/ui/ErrorMessage';
import { libraryService } from '@/services/libraryService';

// Define types
interface LibraryLocation {
  address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  latitude?: number;
  longitude?: number;
}

interface LibraryContact {
  phone?: string;
  email?: string;
  website?: string;
}

interface LibraryProfile {
  id: string;
  name: string;
  location?: LibraryLocation;
  contact?: LibraryContact;
  service_area?: string;
  population_served?: number;
  region?: string;
  available_years: number[];
}

interface LibrarySearchResult {
  total: number;
  libraries: LibraryProfile[];
}

const Libraries: React.FC = () => {
  // State for search and filters
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRegion, setSelectedRegion] = useState('');
  
  // Fetch libraries
  const { data, isLoading, error } = useQuery({
    queryKey: ['libraries', searchQuery, selectedRegion],
    queryFn: async () => {
      return libraryService.searchLibraries({
        query: searchQuery,
        region: selectedRegion,
        limit: 50
      });
    }
  });
  
  // Get unique regions for filter
  const regions = data?.libraries
    ? Array.from(new Set(data.libraries.map((lib: LibraryProfile) => lib.region).filter(Boolean)))
    : [];
  
  // Handle search
  const handleSearch = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    // The search is handled by the useQuery hook
  };
  
  // Handle input change
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };
  
  // Handle region change
  const handleRegionChange = (value: string) => {
    setSelectedRegion(value);
  };
  
  // Handle loading state
  if (isLoading) {
    return (
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-6">Libraries</h1>
        <div className="flex justify-center items-center h-64">
          <LoadingSpinner />
        </div>
      </div>
    );
  }
  
  // Handle error state
  if (error) {
    return (
      <div className="p-6">
        <h1 className="text-2xl font-bold mb-6">Libraries</h1>
        <ErrorMessage message="Failed to load libraries. Please try again later." />
      </div>
    );
  }
  
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Libraries</h1>
      
      {/* Search and filters */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <form onSubmit={handleSearch} className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="col-span-1 md:col-span-2">
            <Input
              type="text"
              placeholder="Search libraries by name or location..."
              value={searchQuery}
              onChange={handleInputChange}
            />
          </div>
          
          <div>
            <Select
              label="Filter by Region"
              value={selectedRegion}
              onChange={handleRegionChange}
              options={[
                { value: '', label: 'All Regions' },
                ...regions.map(region => ({ value: region || '', label: region || 'Unknown' }))
              ]}
            />
          </div>
        </form>
      </div>
      
      {/* Results count */}
      <div className="mb-4">
        <p className="text-gray-600">
          Showing {data?.libraries.length || 0} of {data?.total || 0} libraries
          {searchQuery && ` matching "${searchQuery}"`}
          {selectedRegion && ` in ${selectedRegion}`}
        </p>
      </div>
      
      {/* Library cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {data?.libraries.map((library: LibraryProfile) => (
          <div key={library.id} className="bg-white rounded-lg shadow overflow-hidden">
            <div className="p-4 border-b">
              <h2 className="text-xl font-semibold">{library.name}</h2>
              {library.location && (
                <p className="text-gray-600 mt-1">
                  {[
                    library.location.city,
                    library.location.state
                  ].filter(Boolean).join(', ')}
                </p>
              )}
            </div>
            
            <div className="p-4">
              {library.population_served && (
                <div className="mb-2">
                  <span className="text-sm">
                    Population Served: {library.population_served.toLocaleString()}
                  </span>
                </div>
              )}
              
              {library.service_area && (
                <div className="mb-2">
                  <span className="text-sm">
                    Service Area: {library.service_area}
                  </span>
                </div>
              )}
              
              {library.available_years && library.available_years.length > 0 && (
                <div className="mb-2">
                  <span className="text-sm">
                    Data Years: {Math.min(...library.available_years)} - {Math.max(...library.available_years)}
                  </span>
                </div>
              )}
            </div>
            
            <div className="p-4 bg-gray-50 border-t">
              <Link
                to={`/libraries/${library.id}`}
                className="text-blue-600 hover:text-blue-800 font-medium"
              >
                View Details
              </Link>
            </div>
          </div>
        ))}
      </div>
      
      {/* No results */}
      {data?.libraries.length === 0 && (
        <div className="bg-white rounded-lg shadow p-8 text-center">
          <h3 className="text-lg font-medium text-gray-900 mb-2">No libraries found</h3>
          <p className="text-gray-600">
            Try adjusting your search or filters to find what you're looking for.
          </p>
        </div>
      )}
    </div>
  );
};

export default Libraries; 