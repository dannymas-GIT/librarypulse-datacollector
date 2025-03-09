import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ArrowLeft, MapPin, Phone, Globe, Users, BookOpen, Clock, DollarSign } from 'lucide-react';

// This is a placeholder - we'll implement the actual API service later
const fetchLibraryDetails = async (libraryId: string) => {
  // Simulate API call
  const libraries = {
    'CA0001': {
      library_id: 'CA0001',
      name: 'San Francisco Public Library',
      state: 'CA',
      city: 'San Francisco',
      address: '100 Larkin St',
      zip_code: '94102',
      phone: '(415) 557-4400',
      website: 'https://sfpl.org',
      service_area_population: 870044,
      visits: 5000000,
      total_circulation: 11000000,
      electronic_circulation: 3500000,
      physical_circulation: 7500000,
      total_staff: 650,
      total_operating_revenue: 150000000,
      total_operating_expenditures: 145000000,
      hours_open: 2860,
      outlets: 28
    },
    'NY0001': {
      library_id: 'NY0001',
      name: 'New York Public Library',
      state: 'NY',
      city: 'New York',
      address: '476 5th Ave',
      zip_code: '10018',
      phone: '(917) 275-6975',
      website: 'https://nypl.org',
      service_area_population: 3700000,
      visits: 17000000,
      total_circulation: 24000000,
      electronic_circulation: 8000000,
      physical_circulation: 16000000,
      total_staff: 3200,
      total_operating_revenue: 350000000,
      total_operating_expenditures: 340000000,
      hours_open: 3120,
      outlets: 92
    }
  };
  
  return libraries[libraryId as keyof typeof libraries] || null;
};

const StatItem = ({ icon, label, value }: { icon: React.ReactNode, label: string, value: string | number }) => (
  <div className="flex items-start">
    <div className="p-2 bg-primary-50 rounded-lg mr-3">
      {icon}
    </div>
    <div>
      <p className="text-sm text-gray-500">{label}</p>
      <p className="font-semibold">{value}</p>
    </div>
  </div>
);

const LibraryDetails = () => {
  const { libraryId } = useParams<{ libraryId: string }>();
  
  const { data: library, isLoading, error } = useQuery({
    queryKey: ['library', libraryId],
    queryFn: () => fetchLibraryDetails(libraryId || ''),
    enabled: !!libraryId,
  });

  if (isLoading) {
    return (
      <div className="animate-pulse">
        <div className="h-8 bg-gray-200 rounded w-1/3 mb-6"></div>
        <div className="h-32 bg-gray-200 rounded mb-6"></div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="h-24 bg-gray-200 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  if (error || !library) {
    return (
      <div>
        <Link to="/libraries" className="inline-flex items-center text-primary-600 hover:text-primary-700 mb-6">
          <ArrowLeft className="h-4 w-4 mr-1" />
          <span>Back to Libraries</span>
        </Link>
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          <p>Error loading library details. The library may not exist or there was a problem with the request.</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <Link to="/libraries" className="inline-flex items-center text-primary-600 hover:text-primary-700 mb-6">
        <ArrowLeft className="h-4 w-4 mr-1" />
        <span>Back to Libraries</span>
      </Link>
      
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h1 className="text-2xl font-bold text-primary-700 mb-2">{library.name}</h1>
        <div className="flex flex-wrap items-center text-gray-500 mb-4">
          <div className="flex items-center mr-4">
            <MapPin className="h-4 w-4 mr-1" />
            <span>{library.address}, {library.city}, {library.state} {library.zip_code}</span>
          </div>
          {library.phone && (
            <div className="flex items-center mr-4">
              <Phone className="h-4 w-4 mr-1" />
              <span>{library.phone}</span>
            </div>
          )}
          {library.website && (
            <div className="flex items-center">
              <Globe className="h-4 w-4 mr-1" />
              <a href={library.website} target="_blank" rel="noopener noreferrer" className="text-primary-600 hover:underline">
                Website
              </a>
            </div>
          )}
        </div>
        <p className="text-gray-600">
          Serving a population of {library.service_area_population.toLocaleString()} with {library.outlets} service outlets.
        </p>
      </div>
      
      <h2 className="text-xl font-semibold mb-4">Library Statistics</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatItem 
          icon={<Users className="h-5 w-5 text-primary-600" />}
          label="Annual Visits"
          value={library.visits.toLocaleString()}
        />
        <StatItem 
          icon={<BookOpen className="h-5 w-5 text-primary-600" />}
          label="Total Circulation"
          value={library.total_circulation.toLocaleString()}
        />
        <StatItem 
          icon={<Clock className="h-5 w-5 text-primary-600" />}
          label="Annual Hours Open"
          value={library.hours_open.toLocaleString()}
        />
        <StatItem 
          icon={<Users className="h-5 w-5 text-primary-600" />}
          label="Total Staff (FTE)"
          value={library.total_staff.toLocaleString()}
        />
      </div>
      
      <h2 className="text-xl font-semibold mb-4">Financial Information</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <StatItem 
          icon={<DollarSign className="h-5 w-5 text-primary-600" />}
          label="Operating Revenue"
          value={`$${(library.total_operating_revenue / 1000000).toFixed(1)}M`}
        />
        <StatItem 
          icon={<DollarSign className="h-5 w-5 text-primary-600" />}
          label="Operating Expenditures"
          value={`$${(library.total_operating_expenditures / 1000000).toFixed(1)}M`}
        />
      </div>
    </div>
  );
};

export default LibraryDetails; 