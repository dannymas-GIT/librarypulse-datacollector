import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Search, Filter, MapPin } from 'lucide-react';
import { Link } from 'react-router-dom';

// This is a placeholder - we'll implement the actual API service later
const fetchLibraries = async () => {
  // Simulate API call
  return [
    { library_id: 'CA0001', name: 'San Francisco Public Library', state: 'CA', city: 'San Francisco', visits: 5000000 },
    { library_id: 'NY0001', name: 'New York Public Library', state: 'NY', city: 'New York', visits: 17000000 },
    { library_id: 'IL0001', name: 'Chicago Public Library', state: 'IL', city: 'Chicago', visits: 9000000 },
    { library_id: 'TX0001', name: 'Houston Public Library', state: 'TX', city: 'Houston', visits: 7000000 },
    { library_id: 'WA0001', name: 'Seattle Public Library', state: 'WA', city: 'Seattle', visits: 4000000 },
  ];
};

const Libraries = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedState, setSelectedState] = useState('');

  const { data: libraries = [], isLoading, error } = useQuery({
    queryKey: ['libraries'],
    queryFn: fetchLibraries,
  });

  const filteredLibraries = libraries.filter(library => {
    const matchesSearch = library.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesState = selectedState ? library.state === selectedState : true;
    return matchesSearch && matchesState;
  });

  const states = [...new Set(libraries.map(library => library.state))].sort();

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Libraries</h1>

      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <span className="absolute inset-y-0 left-0 flex items-center pl-3">
                <Search className="h-5 w-5 text-gray-400" />
              </span>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="block w-full rounded-md border-0 py-2 pl-10 pr-4 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-500 sm:text-sm"
                placeholder="Search libraries..."
              />
            </div>
          </div>
          <div className="w-full md:w-64">
            <div className="relative">
              <span className="absolute inset-y-0 left-0 flex items-center pl-3">
                <Filter className="h-5 w-5 text-gray-400" />
              </span>
              <select
                value={selectedState}
                onChange={(e) => setSelectedState(e.target.value)}
                className="block w-full rounded-md border-0 py-2 pl-10 pr-4 text-gray-900 ring-1 ring-inset ring-gray-300 focus:ring-2 focus:ring-inset focus:ring-primary-500 sm:text-sm"
              >
                <option value="">All States</option>
                {states.map(state => (
                  <option key={state} value={state}>{state}</option>
                ))}
              </select>
            </div>
          </div>
        </div>
      </div>

      {isLoading ? (
        <div className="animate-pulse space-y-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="bg-gray-200 h-24 rounded-lg"></div>
          ))}
        </div>
      ) : error ? (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          <p>Error loading libraries. Please try again later.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredLibraries.length === 0 ? (
            <div className="bg-white rounded-lg shadow p-6 text-center">
              <p className="text-gray-500">No libraries found matching your criteria.</p>
            </div>
          ) : (
            filteredLibraries.map(library => (
              <Link
                key={library.library_id}
                to={`/libraries/${library.library_id}`}
                className="block bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <h2 className="text-lg font-semibold text-primary-700">{library.name}</h2>
                    <div className="flex items-center text-gray-500 mt-1">
                      <MapPin className="h-4 w-4 mr-1" />
                      <span>{library.city}, {library.state}</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-gray-500">Annual Visits</div>
                    <div className="font-semibold">{library.visits.toLocaleString()}</div>
                  </div>
                </div>
              </Link>
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default Libraries; 