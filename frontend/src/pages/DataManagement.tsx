import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Download, RefreshCw, AlertCircle, CheckCircle, Clock } from 'lucide-react';

// This is a placeholder - we'll implement the actual API service later
const fetchDatasetStatus = async () => {
  // Simulate API call
  return {
    2022: { status: 'complete', record_count: 9000, updated_at: '2023-10-15T14:30:00Z' },
    2021: { status: 'complete', record_count: 8950, updated_at: '2023-08-20T10:15:00Z' },
    2020: { status: 'complete', record_count: 8900, updated_at: '2023-08-20T10:15:00Z' },
    2019: { status: 'complete', record_count: 8850, updated_at: '2023-08-20T10:15:00Z' },
    2018: { status: 'complete', record_count: 8800, updated_at: '2023-08-20T10:15:00Z' },
  };
};

const DataManagement = () => {
  const [isUpdating, setIsUpdating] = useState(false);
  const [isCollecting, setIsCollecting] = useState(false);
  const [selectedYear, setSelectedYear] = useState<number | null>(null);
  
  const { data: datasets = {}, isLoading, error, refetch } = useQuery({
    queryKey: ['datasetStatus'],
    queryFn: fetchDatasetStatus,
  });

  const handleUpdate = () => {
    setIsUpdating(true);
    // Simulate API call
    setTimeout(() => {
      setIsUpdating(false);
      refetch();
    }, 2000);
  };

  const handleCollectYear = (year: number) => {
    setSelectedYear(year);
    setIsCollecting(true);
    // Simulate API call
    setTimeout(() => {
      setIsCollecting(false);
      setSelectedYear(null);
      refetch();
    }, 2000);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'complete':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'pending':
      case 'processing':
        return <Clock className="h-5 w-5 text-amber-500" />;
      case 'error':
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      default:
        return null;
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">Data Management</h1>
      
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6">
          <div>
            <h2 className="text-lg font-semibold">IMLS Public Libraries Survey Data</h2>
            <p className="text-gray-600">Manage the PLS data available in the system.</p>
          </div>
          <button
            onClick={handleUpdate}
            disabled={isUpdating}
            className={`mt-4 md:mt-0 inline-flex items-center px-4 py-2 rounded-md ${
              isUpdating
                ? 'bg-gray-300 text-gray-700 cursor-not-allowed'
                : 'bg-primary-600 text-white hover:bg-primary-700'
            }`}
          >
            <RefreshCw className={`h-5 w-5 mr-2 ${isUpdating ? 'animate-spin' : ''}`} />
            <span>{isUpdating ? 'Checking for updates...' : 'Check for updates'}</span>
          </button>
        </div>
        
        {isLoading ? (
          <div className="animate-pulse space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-16 bg-gray-200 rounded"></div>
            ))}
          </div>
        ) : error ? (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            <p>Error loading dataset status. Please try again later.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Year
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Records
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Last Updated
                  </th>
                  <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {Object.entries(datasets).map(([year, data]) => (
                  <tr key={year}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {year}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      <div className="flex items-center">
                        {getStatusIcon(data.status)}
                        <span className="ml-2 capitalize">{data.status}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {data.record_count?.toLocaleString() || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {data.updated_at ? formatDate(data.updated_at) : '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        onClick={() => handleCollectYear(parseInt(year))}
                        disabled={isCollecting && selectedYear === parseInt(year)}
                        className={`inline-flex items-center px-3 py-1 rounded-md ${
                          isCollecting && selectedYear === parseInt(year)
                            ? 'bg-gray-300 text-gray-700 cursor-not-allowed'
                            : 'bg-primary-50 text-primary-700 hover:bg-primary-100'
                        }`}
                      >
                        <Download className="h-4 w-4 mr-1" />
                        <span>
                          {isCollecting && selectedYear === parseInt(year)
                            ? 'Collecting...'
                            : 'Collect'
                          }
                        </span>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
      
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold mb-4">About the Data</h2>
        <p className="text-gray-600 mb-4">
          The Public Libraries Survey (PLS) is conducted annually by the Institute of Museum and Library Services (IMLS).
          The survey collects data from approximately 9,000 public libraries across the United States.
        </p>
        <p className="text-gray-600">
          Data is typically released with a 1-2 year lag. The most recent data available is usually from the previous fiscal year.
          Use the controls above to check for updates and collect data for specific years.
        </p>
      </div>
    </div>
  );
};

export default DataManagement; 