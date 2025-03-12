import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Input } from '@/components/ui/Input';
import { Select } from '@/components/ui/Select';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { ErrorMessage } from '@/components/ui/ErrorMessage';
import { Pagination } from '@/components/ui/Pagination';
import { Card } from '@/components/ui/Card';
import { libraryService } from '@/services/libraryService';
import { Library, Users, MapPin, Phone, Globe, BookOpen } from 'lucide-react';

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
  total_circulation?: number;
  visits?: number;
}

interface LibrarySearchResult {
  total: number;
  libraries: LibraryProfile[];
}

interface SearchFilters {
  query: string;
  region: string;
  state: string;
  sortBy: string;
  page: number;
  limit: number;
}

const Libraries: React.FC = () => {
  // State for search and filters
  const [filters, setFilters] = useState<SearchFilters>({
    query: '',
    region: '',
    state: '',
    sortBy: 'name',
    page: 1,
    limit: 12
  });
  
  // Temporary search query for the input field
  const [tempQuery, setTempQuery] = useState('');
  
  // Fetch libraries
  const { data, isLoading, error } = useQuery({
    queryKey: ['libraries', filters],
    queryFn: async () => {
      return libraryService.searchLibraries({
        query: filters.query,
        region: filters.region,
        state: filters.state,
        limit: filters.limit,
        offset: (filters.page - 1) * filters.limit
      });
    }
  });
  
  // Get unique regions for filter
  const regions = data?.libraries
    ? Array.from(new Set(data.libraries.map((lib: LibraryProfile) => lib.region).filter(Boolean)))
    : [];
  
  // Get unique states for filter
  const states = [
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 
    'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 
    'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 
    'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 
    'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
  ];
  
  // Sort options
  const sortOptions = [
    { value: 'name', label: 'Name (A-Z)' },
    { value: 'name_desc', label: 'Name (Z-A)' },
    { value: 'population', label: 'Population (High to Low)' },
    { value: 'population_asc', label: 'Population (Low to High)' }
  ];
  
  // Handle search
  const handleSearch = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setFilters({
      ...filters,
      query: tempQuery,
      page: 1 // Reset to first page on new search
    });
  };
  
  // Handle input change
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setTempQuery(e.target.value);
  };
  
  // Handle filter changes
  const handleFilterChange = (key: keyof SearchFilters, value: string | number) => {
    setFilters({
      ...filters,
      [key]: value,
      page: key !== 'page' ? 1 : value // Reset to first page on filter change, unless changing page
    });
  };
  
  // Calculate total pages
  const totalPages = data ? Math.ceil(data.total / filters.limit) : 0;
  
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
      <Card className="p-4 mb-6">
        <form onSubmit={handleSearch} className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="col-span-1 md:col-span-2">
            <Input
              type="text"
              placeholder="Search libraries by name or location..."
              value={tempQuery}
              onChange={handleInputChange}
            />
          </div>
          
          <div>
            <Select
              label="State"
              value={filters.state}
              onChange={(value) => handleFilterChange('state', value)}
              options={[
                { value: '', label: 'All States' },
                ...states.map(state => ({ value: state, label: state }))
              ]}
            />
          </div>
          
          <div>
            <Select
              label="Region"
              value={filters.region}
              onChange={(value) => handleFilterChange('region', value)}
              options={[
                { value: '', label: 'All Regions' },
                ...regions.map(region => ({ value: region || '', label: region || 'Unknown' }))
              ]}
            />
          </div>
          
          <div className="col-span-1 md:col-span-2">
            <button 
              type="submit" 
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded"
            >
              Search
            </button>
          </div>
          
          <div className="col-span-1 md:col-span-2">
            <Select
              label="Sort By"
              value={filters.sortBy}
              onChange={(value) => handleFilterChange('sortBy', value)}
              options={sortOptions}
            />
          </div>
        </form>
      </Card>
      
      {/* Results count */}
      <div className="mb-4">
        <p className="text-gray-600">
          Showing {data?.libraries.length || 0} of {data?.total || 0} libraries
          {filters.query && ` matching "${filters.query}"`}
          {filters.state && ` in ${filters.state}`}
          {filters.region && ` in ${filters.region} region`}
        </p>
      </div>
      
      {/* Library cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {data?.libraries.map((library: LibraryProfile) => (
          <Card key={library.id} className="overflow-hidden flex flex-col">
            <div className="p-4 border-b bg-blue-50">
              <div className="flex items-start">
                <div className="p-2 bg-blue-100 rounded-full mr-3">
                  <Library className="h-5 w-5 text-blue-700" />
                </div>
                <div>
                  <h2 className="text-xl font-semibold">{library.name}</h2>
                  {library.location && (
                    <p className="text-gray-600 mt-1 flex items-center">
                      <MapPin className="h-4 w-4 mr-1" />
                      {[
                        library.location.city,
                        library.location.state
                      ].filter(Boolean).join(', ')}
                    </p>
                  )}
                </div>
              </div>
            </div>
            
            <div className="p-4 flex-grow">
              <div className="grid grid-cols-2 gap-4">
                {library.population_served && (
                  <div className="flex items-center">
                    <Users className="h-4 w-4 text-gray-500 mr-2" />
                    <span className="text-sm">
                      {library.population_served.toLocaleString()} served
                    </span>
                  </div>
                )}
                
                {library.region && (
                  <div className="flex items-center">
                    <MapPin className="h-4 w-4 text-gray-500 mr-2" />
                    <span className="text-sm">
                      {library.region} region
                    </span>
                  </div>
                )}
                
                {library.contact?.phone && (
                  <div className="flex items-center">
                    <Phone className="h-4 w-4 text-gray-500 mr-2" />
                    <span className="text-sm truncate">
                      {library.contact.phone}
                    </span>
                  </div>
                )}
                
                {library.contact?.website && (
                  <div className="flex items-center">
                    <Globe className="h-4 w-4 text-gray-500 mr-2" />
                    <span className="text-sm truncate">
                      Website
                    </span>
                  </div>
                )}
              </div>
              
              {library.available_years && library.available_years.length > 0 && (
                <div className="mt-4 pt-4 border-t">
                  <div className="flex items-center mb-2">
                    <BookOpen className="h-4 w-4 text-gray-500 mr-2" />
                    <span className="text-sm font-medium">
                      Data available: {Math.min(...library.available_years)} - {Math.max(...library.available_years)}
                    </span>
                  </div>
                  
                  {library.total_circulation && (
                    <div className="text-sm text-gray-600 ml-6">
                      Latest circulation: {library.total_circulation.toLocaleString()} items
                    </div>
                  )}
                  
                  {library.visits && (
                    <div className="text-sm text-gray-600 ml-6">
                      Latest visits: {library.visits.toLocaleString()}
                    </div>
                  )}
                </div>
              )}
            </div>
            
            <div className="p-4 bg-gray-50 border-t mt-auto">
              <Link
                to={`/libraries/${library.id}`}
                className="block w-full bg-blue-600 hover:bg-blue-700 text-white text-center font-medium py-2 px-4 rounded"
              >
                View Details
              </Link>
            </div>
          </Card>
        ))}
      </div>
      
      {/* No results */}
      {data?.libraries.length === 0 && (
        <Card className="p-8 text-center">
          <h3 className="text-lg font-medium text-gray-900 mb-2">No libraries found</h3>
          <p className="text-gray-600">
            Try adjusting your search or filters to find what you're looking for.
          </p>
        </Card>
      )}
      
      {/* Pagination */}
      {totalPages > 1 && (
        <div className="mt-6 flex justify-center">
          <Pagination
            currentPage={filters.page}
            totalPages={totalPages}
            onPageChange={(page) => handleFilterChange('page', page)}
          />
        </div>
      )}
    </div>
  );
};

export default Libraries; 