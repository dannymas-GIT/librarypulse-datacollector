import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ArrowLeft, MapPin, Phone, Globe, Users, BookOpen, Clock, DollarSign } from 'lucide-react';
import { libraryService } from '@/services/libraryService';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { ErrorMessage } from '@/components/ui/ErrorMessage';

// Define the StatItem component for displaying statistics
const StatItem = ({ label, value }: { label: string, value: string | number }) => (
  <div className="bg-white p-4 rounded-lg shadow">
    <p className="text-sm text-gray-500">{label}</p>
    <p className="text-xl font-semibold">{value}</p>
  </div>
);

const LibraryDetails = () => {
  const { libraryId } = useParams<{ libraryId: string }>();
  
  // Fetch library details
  const { data: library, isLoading, error } = useQuery({
    queryKey: ['library', libraryId],
    queryFn: () => libraryService.getLibrary(libraryId || ''),
    enabled: !!libraryId,
  });

  // Fetch library statistics (this would be implemented in a real API)
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['libraryStats', libraryId],
    queryFn: async () => {
      // This is a placeholder for actual API call
      // In a real implementation, we would fetch this from the API
      return {
        visits: 125000,
        total_circulation: 250000,
        electronic_circulation: 75000,
        physical_circulation: 175000,
        total_staff: 25,
        total_operating_revenue: 2500000,
        total_operating_expenditures: 2400000,
        hours_open: 2500,
        outlets: 3
      };
    },
    enabled: !!libraryId,
  });

  if (isLoading || statsLoading) {
    return (
      <div className="p-6">
        <Link to="/libraries" className="inline-flex items-center text-blue-600 hover:text-blue-800 mb-6">
          <ArrowLeft className="h-4 w-4 mr-1" />
          <span>Back to Libraries</span>
        </Link>
        <div className="flex justify-center items-center h-64">
          <LoadingSpinner />
        </div>
      </div>
    );
  }

  if (error || !library) {
    return (
      <div className="p-6">
        <Link to="/libraries" className="inline-flex items-center text-blue-600 hover:text-blue-800 mb-6">
          <ArrowLeft className="h-4 w-4 mr-1" />
          <span>Back to Libraries</span>
        </Link>
        <ErrorMessage message="Error loading library details. The library may not exist or there was a problem with the request." />
      </div>
    );
  }

  return (
    <div className="p-6">
      <Link to="/libraries" className="inline-flex items-center text-blue-600 hover:text-blue-800 mb-6">
        <ArrowLeft className="h-4 w-4 mr-1" />
        <span>Back to Libraries</span>
      </Link>
      
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h1 className="text-2xl font-bold text-gray-800 mb-2">{library.name}</h1>
        {library.location && (
          <div className="text-gray-600 mb-4">
            {[
              library.location.address,
              library.location.city,
              library.location.state,
              library.location.zip_code
            ].filter(Boolean).join(', ')}
          </div>
        )}
        
        {library.contact && (
          <div className="space-y-2 mb-4">
            {library.contact.phone && (
              <div className="text-gray-600">
                Phone: {library.contact.phone}
              </div>
            )}
            {library.contact.website && (
              <div>
                <a 
                  href={library.contact.website} 
                  target="_blank" 
                  rel="noopener noreferrer" 
                  className="text-blue-600 hover:underline"
                >
                  Visit Website
                </a>
              </div>
            )}
          </div>
        )}
        
        {library.population_served && (
          <p className="text-gray-600">
            Serving a population of {library.population_served.toLocaleString()}
          </p>
        )}
      </div>
      
      {stats && (
        <>
          <h2 className="text-xl font-semibold mb-4">Library Statistics</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <StatItem 
              label="Annual Visits"
              value={stats.visits.toLocaleString()}
            />
            <StatItem 
              label="Total Circulation"
              value={stats.total_circulation.toLocaleString()}
            />
            <StatItem 
              label="Electronic Circulation"
              value={stats.electronic_circulation.toLocaleString()}
            />
            <StatItem 
              label="Physical Circulation"
              value={stats.physical_circulation.toLocaleString()}
            />
          </div>
          
          <h2 className="text-xl font-semibold mb-4">Financial Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <StatItem 
              label="Operating Revenue"
              value={`$${(stats.total_operating_revenue / 1000000).toFixed(1)}M`}
            />
            <StatItem 
              label="Operating Expenditures"
              value={`$${(stats.total_operating_expenditures / 1000000).toFixed(1)}M`}
            />
          </div>
        </>
      )}
    </div>
  );
};

export default LibraryDetails; 