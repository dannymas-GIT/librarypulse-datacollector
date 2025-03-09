import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Search, Plus, X, BarChart3 } from 'lucide-react';

import { fetchComparisonStats } from '@/services/statsService';

const Comparison = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedLibraries, setSelectedLibraries] = useState<string[]>(['CA0001', 'NY0001']);
  const [selectedYear, setSelectedYear] = useState<number>(2022);
  
  const { data, isLoading, error } = useQuery({
    queryKey: ['comparisonStats', selectedLibraries, selectedYear],
    queryFn: () => fetchComparisonStats(selectedLibraries, selectedYear),
    enabled: selectedLibraries.length > 0,
  });

  // Placeholder for search results
  const searchResults = [
    { library_id: 'CA0001', name: 'San Francisco Public Library', state: 'CA' },
    { library_id: 'NY0001', name: 'New York Public Library', state: 'NY' },
    { library_id: 'IL0001', name: 'Chicago Public Library', state: 'IL' },
    { library_id: 'TX0001', name: 'Houston Public Library', state: 'TX' },
    { library_id: 'WA0001', name: 'Seattle Public Library', state: 'WA' },
  ].filter(library => 
    library.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    library.state.toLowerCase().includes(searchQuery.toLowerCase())
  );
  
  // Placeholder for year list
  const years = [2022, 2021, 2020, 2019, 2018];

  const addLibrary = (libraryId: string) => {
    if (!selectedLibraries.includes(libraryId)) {
      setSelectedLibraries([...selectedLibraries, libraryId]);
    }
    setSearchQuery('');
  };

  const removeLibrary = (libraryId: string) => {
    setSelectedLibraries(selectedLibraries.filter(id => id !== libraryId));
  };

  // Placeholder for chart - in a real implementation, we would use Chart.js or a similar library
  const renderComparisonChart = () => {
    if (!data) return null;
    
    return (
      <div className="bg-white p-6 rounded-lg shadow">
        <div className="h-80 flex items-center justify-center border border-gray-200 rounded-lg">
          <div className="text-center">
            <BarChart3 className="h-12 w-12 text-primary-500 mx-auto mb-4" />
            <p className="text-gray-500">
              Comparison chart would be rendered here for {data.libraries.length} libraries
            </p>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Library Comparison</h1>
      
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex flex-col md:flex-row gap-4 justify-between">
          <div className="flex-1">
            <h2 className="text-lg font-semibold mb-2">Select Libraries to Compare</h2>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 flex items-center pl-3">
                <Search className="h-5 w-5 text-gray-400" />
              </span>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="block w-full rounded-md border-0 py-2 pl-10 pr-4 text-gray-900 ring-1 ring-inset ring-gray-300 placeholder:text-gray-400 focus:ring-2 focus:ring-inset focus:ring-primary-500 sm:text-sm"
                placeholder="Search libraries by name or state..."
              />
            </div>
            
            {searchQuery && (
              <div className="mt-2 border rounded-md shadow-sm max-h-60 overflow-y-auto">
                {searchResults.length === 0 ? (
                  <div className="p-3 text-gray-500">No libraries found</div>
                ) : (
                  <ul className="divide-y divide-gray-200">
                    {searchResults.map(library => (
                      <li key={library.library_id} className="p-3 hover:bg-gray-50">
                        <button
                          onClick={() => addLibrary(library.library_id)}
                          className="w-full flex items-center justify-between"
                          disabled={selectedLibraries.includes(library.library_id)}
                        >
                          <div className="text-left">
                            <div className="font-medium">{library.name}</div>
                            <div className="text-sm text-gray-500">{library.state}</div>
                          </div>
                          <Plus className={`h-5 w-5 ${selectedLibraries.includes(library.library_id) ? 'text-gray-300' : 'text-primary-500'}`} />
                        </button>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            )}
          </div>
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
        </div>
        
        <div className="mt-4">
          <h3 className="text-sm font-medium text-gray-700 mb-2">Selected Libraries:</h3>
          <div className="flex flex-wrap gap-2">
            {selectedLibraries.length === 0 ? (
              <div className="text-gray-500">No libraries selected</div>
            ) : (
              data?.libraries.map(library => (
                <div key={library.library_id} className="inline-flex items-center bg-primary-50 text-primary-700 rounded-full pl-3 pr-1 py-1">
                  <span className="mr-1">{library.name}</span>
                  <button
                    onClick={() => removeLibrary(library.library_id)}
                    className="p-1 rounded-full hover:bg-primary-100"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
      
      {isLoading ? (
        <div className="animate-pulse space-y-6">
          <div className="h-80 bg-gray-200 rounded-lg"></div>
          <div className="h-60 bg-gray-200 rounded-lg"></div>
        </div>
      ) : error ? (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          <p>Error loading comparison data. Please try again later.</p>
        </div>
      ) : selectedLibraries.length === 0 ? (
        <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded">
          <p>Please select at least one library to compare.</p>
        </div>
      ) : (
        <>
          {renderComparisonChart()}
          
          <div className="mt-6 bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4">Comparison Table</h2>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Metric
                    </th>
                    {data?.libraries.map(library => (
                      <th key={library.library_id} scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        {library.name}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {data && Object.entries(data.metric_definitions).map(([metricKey, metricName]) => (
                    <tr key={metricKey}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {metricName}
                      </td>
                      {data.libraries.map(library => (
                        <td key={`${library.library_id}-${metricKey}`} className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {library.metrics[metricKey]?.value.toLocaleString() || '-'}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default Comparison; 