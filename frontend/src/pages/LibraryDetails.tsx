import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ArrowLeft, MapPin, Phone, Globe, Users, BookOpen, Clock, DollarSign, Mail, Calendar, BarChart2, TrendingUp, Building } from 'lucide-react';
import { libraryService } from '@/services/libraryService';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { ErrorMessage } from '@/components/ui/ErrorMessage';
import { Card } from '@/components/ui/Card';
import { Select } from '@/components/ui/Select';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { useState } from 'react';
import { DemographicDataPanel } from '@/components/demographics';

// Define the StatItem component for displaying statistics
const StatItem = ({ label, value, icon }: { label: string, value: string | number, icon: React.ReactNode }) => (
  <Card className="p-4">
    <div className="flex items-center">
      <div className="p-2 bg-blue-100 rounded-full mr-3">
        {icon}
      </div>
      <div>
        <p className="text-sm text-gray-500">{label}</p>
        <p className="text-xl font-semibold">{value}</p>
      </div>
    </div>
  </Card>
);

// Format numbers for display
const formatNumber = (num: number): string => {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M';
  } else if (num >= 1000) {
    return (num / 1000).toFixed(1) + 'K';
  } else {
    return num.toString();
  }
};

// Colors for charts
const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

const LibraryDetails = () => {
  const { libraryId } = useParams<{ libraryId: string }>();
  const [selectedYear, setSelectedYear] = useState<number>(2022);
  
  // Fetch library details
  const { data: library, isLoading, error } = useQuery({
    queryKey: ['library', libraryId],
    queryFn: () => libraryService.getLibrary(libraryId || ''),
    enabled: !!libraryId,
  });

  // Fetch library statistics (this would be implemented in a real API)
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['libraryStats', libraryId, selectedYear],
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
        outlets: 3,
        total_programs: 480,
        program_attendance: 13500,
        registered_users: 45000,
        collection_expenditures: 400000,
        staff_expenditures: 1500000,
        electronic_expenditures: 300000,
        print_collection: 120000,
        electronic_collection: 50000,
        audio_collection: 15000,
        video_collection: 10000
      };
    },
    enabled: !!libraryId,
  });

  // Fetch historical data for charts
  const { data: historicalData, isLoading: historicalLoading } = useQuery({
    queryKey: ['libraryHistorical', libraryId],
    queryFn: async () => {
      // This is a placeholder for actual API call
      return {
        years: [2018, 2019, 2020, 2021, 2022],
        metrics: {
          visits: [110000, 115000, 105000, 120000, 125000],
          total_circulation: [230000, 235000, 240000, 245000, 250000],
          electronic_circulation: [50000, 55000, 65000, 70000, 75000],
          physical_circulation: [180000, 180000, 175000, 175000, 175000],
          total_programs: [450, 460, 470, 475, 480],
          program_attendance: [12000, 12500, 13000, 13200, 13500]
        }
      };
    },
    enabled: !!libraryId,
  });

  // Available years for selection
  const years = [2018, 2019, 2020, 2021, 2022];

  // Handle year change
  const handleYearChange = (value: string) => {
    setSelectedYear(parseInt(value));
  };

  // Prepare data for circulation breakdown pie chart
  const circulationData = stats ? [
    { name: 'Physical', value: stats.physical_circulation },
    { name: 'Electronic', value: stats.electronic_circulation }
  ] : [];

  // Prepare data for expenditure breakdown pie chart
  const expenditureData = stats ? [
    { name: 'Staff', value: stats.staff_expenditures },
    { name: 'Collection', value: stats.collection_expenditures },
    { name: 'Electronic', value: stats.electronic_expenditures },
    { name: 'Other', value: stats.total_operating_expenditures - stats.staff_expenditures - stats.collection_expenditures - stats.electronic_expenditures }
  ] : [];

  // Prepare data for collection breakdown pie chart
  const collectionData = stats ? [
    { name: 'Print', value: stats.print_collection },
    { name: 'Electronic', value: stats.electronic_collection },
    { name: 'Audio', value: stats.audio_collection },
    { name: 'Video', value: stats.video_collection }
  ] : [];

  if (isLoading || statsLoading || historicalLoading) {
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
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <Link to="/libraries" className="text-blue-600 hover:text-blue-800 flex items-center">
          <ArrowLeft className="h-4 w-4 mr-1" />
          Back to Libraries
        </Link>
      </div>

      <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
        <h1 className="text-3xl font-bold mb-2 md:mb-0">{library.name}</h1>
        <div className="flex items-center">
          <span className="mr-2">Year:</span>
          <Select
            value={selectedYear.toString()}
            onChange={(e) => setSelectedYear(Number(e.target.value))}
            options={[
              { value: '2018', label: '2018' },
              { value: '2019', label: '2019' },
              { value: '2020', label: '2020' },
              { value: '2021', label: '2021' },
              { value: '2022', label: '2022' },
            ]}
            className="w-24"
          />
        </div>
      </div>

      {statsLoading || historicalLoading ? (
        <LoadingSpinner />
      ) : (
        <>
          <Card className="p-6 mb-6">
            <div className="flex flex-col md:flex-row">
              <div className="md:w-2/3">
                <h1 className="text-2xl font-bold text-gray-800 mb-2">{library.name}</h1>
                {library.location && (
                  <div className="flex items-start mb-4">
                    <MapPin className="h-5 w-5 text-gray-500 mr-2 mt-0.5" />
                    <div>
                      {library.location.address && <div>{library.location.address}</div>}
                      <div>
                        {[
                          library.location.city,
                          library.location.state,
                          library.location.zip_code
                        ].filter(Boolean).join(', ')}
                      </div>
                    </div>
                  </div>
                )}
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  {library.contact?.phone && (
                    <div className="flex items-center">
                      <Phone className="h-5 w-5 text-gray-500 mr-2" />
                      <span>{library.contact.phone}</span>
                    </div>
                  )}
                  
                  {library.contact?.email && (
                    <div className="flex items-center">
                      <Mail className="h-5 w-5 text-gray-500 mr-2" />
                      <span>{library.contact.email}</span>
                    </div>
                  )}
                  
                  {library.contact?.website && (
                    <div className="flex items-center">
                      <Globe className="h-5 w-5 text-gray-500 mr-2" />
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
                  
                  {library.population_served && (
                    <div className="flex items-center">
                      <Users className="h-5 w-5 text-gray-500 mr-2" />
                      <span>Serving {library.population_served.toLocaleString()} people</span>
                    </div>
                  )}
                </div>
              </div>
              
              <div className="md:w-1/3 mt-4 md:mt-0 md:border-l md:pl-6">
                <h2 className="text-lg font-semibold mb-3">Quick Facts</h2>
                <ul className="space-y-2">
                  {stats?.outlets && (
                    <li className="flex items-center">
                      <Building className="h-4 w-4 text-gray-500 mr-2" />
                      <span>{stats.outlets} {stats.outlets === 1 ? 'Branch' : 'Branches'}</span>
                    </li>
                  )}
                  {stats?.hours_open && (
                    <li className="flex items-center">
                      <Clock className="h-4 w-4 text-gray-500 mr-2" />
                      <span>{stats.hours_open.toLocaleString()} Annual Hours Open</span>
                    </li>
                  )}
                  {stats?.total_staff && (
                    <li className="flex items-center">
                      <Users className="h-4 w-4 text-gray-500 mr-2" />
                      <span>{stats.total_staff} Staff Members</span>
                    </li>
                  )}
                  {library.available_years && library.available_years.length > 0 && (
                    <li className="flex items-center">
                      <Calendar className="h-4 w-4 text-gray-500 mr-2" />
                      <span>Data available from {Math.min(...library.available_years)} to {Math.max(...library.available_years)}</span>
                    </li>
                  )}
                </ul>
              </div>
            </div>
          </Card>
          
          {/* Demographics Section */}
          <h2 className="text-xl font-semibold mb-4 mt-8">Community Demographics</h2>
          <div className="mb-8">
            <DemographicDataPanel libraryId={libraryId} />
          </div>
          
          {/* Key Statistics */}
          <h2 className="text-xl font-semibold mb-4">Key Statistics ({selectedYear})</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <StatItem 
              label="Annual Visits"
              value={stats.visits.toLocaleString()}
              icon={<Users className="h-5 w-5 text-blue-700" />}
            />
            <StatItem 
              label="Total Circulation"
              value={stats.total_circulation.toLocaleString()}
              icon={<BookOpen className="h-5 w-5 text-blue-700" />}
            />
            <StatItem 
              label="Total Programs"
              value={stats.total_programs.toLocaleString()}
              icon={<Calendar className="h-5 w-5 text-blue-700" />}
            />
            <StatItem 
              label="Program Attendance"
              value={stats.program_attendance.toLocaleString()}
              icon={<Users className="h-5 w-5 text-blue-700" />}
            />
          </div>
          
          {/* Historical Trends Chart */}
          {historicalData && (
            <Card className="p-6 mb-8">
              <h2 className="text-xl font-semibold mb-4">Historical Trends</h2>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={historicalData.years.map((year, index) => ({
                      year,
                      visits: historicalData.metrics.visits[index],
                      circulation: historicalData.metrics.total_circulation[index],
                      electronic: historicalData.metrics.electronic_circulation[index],
                      physical: historicalData.metrics.physical_circulation[index]
                    }))}
                    margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="year" />
                    <YAxis />
                    <Tooltip formatter={(value) => value.toLocaleString()} />
                    <Legend />
                    <Line type="monotone" dataKey="visits" stroke="#8884d8" name="Visits" />
                    <Line type="monotone" dataKey="circulation" stroke="#82ca9d" name="Total Circulation" />
                    <Line type="monotone" dataKey="electronic" stroke="#ffc658" name="Electronic Circulation" />
                    <Line type="monotone" dataKey="physical" stroke="#ff8042" name="Physical Circulation" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </Card>
          )}
          
          {/* Breakdown Charts */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {/* Circulation Breakdown */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Circulation Breakdown</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={circulationData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {circulationData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => value.toLocaleString()} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </Card>
            
            {/* Expenditure Breakdown */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Expenditure Breakdown</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={expenditureData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {expenditureData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => `$${(value / 1000000).toFixed(2)}M`} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </Card>
            
            {/* Collection Breakdown */}
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Collection Breakdown</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={collectionData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {collectionData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => value.toLocaleString()} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </Card>
          </div>
          
          <h2 className="text-xl font-semibold mb-4">Financial Information</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <StatItem 
              label="Operating Revenue"
              value={`$${(stats.total_operating_revenue / 1000000).toFixed(1)}M`}
              icon={<DollarSign className="h-5 w-5 text-blue-700" />}
            />
            <StatItem 
              label="Operating Expenditures"
              value={`$${(stats.total_operating_expenditures / 1000000).toFixed(1)}M`}
              icon={<DollarSign className="h-5 w-5 text-blue-700" />}
            />
          </div>
          
          <Card className="p-6 mb-8">
            <h2 className="text-xl font-semibold mb-4">Detailed Statistics</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-medium text-gray-700 mb-2">Circulation</h3>
                <ul className="space-y-2">
                  <li className="flex justify-between">
                    <span className="text-gray-600">Total Circulation</span>
                    <span className="font-medium">{stats.total_circulation.toLocaleString()}</span>
                  </li>
                  <li className="flex justify-between">
                    <span className="text-gray-600">Physical Circulation</span>
                    <span className="font-medium">{stats.physical_circulation.toLocaleString()}</span>
                  </li>
                  <li className="flex justify-between">
                    <span className="text-gray-600">Electronic Circulation</span>
                    <span className="font-medium">{stats.electronic_circulation.toLocaleString()}</span>
                  </li>
                </ul>
              </div>
              
              <div>
                <h3 className="text-lg font-medium text-gray-700 mb-2">Programs</h3>
                <ul className="space-y-2">
                  <li className="flex justify-between">
                    <span className="text-gray-600">Total Programs</span>
                    <span className="font-medium">{stats.total_programs.toLocaleString()}</span>
                  </li>
                  <li className="flex justify-between">
                    <span className="text-gray-600">Program Attendance</span>
                    <span className="font-medium">{stats.program_attendance.toLocaleString()}</span>
                  </li>
                  <li className="flex justify-between">
                    <span className="text-gray-600">Avg. Attendance per Program</span>
                    <span className="font-medium">{(stats.program_attendance / stats.total_programs).toFixed(1)}</span>
                  </li>
                </ul>
              </div>
              
              <div>
                <h3 className="text-lg font-medium text-gray-700 mb-2">Collection</h3>
                <ul className="space-y-2">
                  <li className="flex justify-between">
                    <span className="text-gray-600">Print Collection</span>
                    <span className="font-medium">{stats.print_collection.toLocaleString()}</span>
                  </li>
                  <li className="flex justify-between">
                    <span className="text-gray-600">Electronic Collection</span>
                    <span className="font-medium">{stats.electronic_collection.toLocaleString()}</span>
                  </li>
                  <li className="flex justify-between">
                    <span className="text-gray-600">Audio Collection</span>
                    <span className="font-medium">{stats.audio_collection.toLocaleString()}</span>
                  </li>
                  <li className="flex justify-between">
                    <span className="text-gray-600">Video Collection</span>
                    <span className="font-medium">{stats.video_collection.toLocaleString()}</span>
                  </li>
                </ul>
              </div>
              
              <div>
                <h3 className="text-lg font-medium text-gray-700 mb-2">Financial</h3>
                <ul className="space-y-2">
                  <li className="flex justify-between">
                    <span className="text-gray-600">Total Revenue</span>
                    <span className="font-medium">${stats.total_operating_revenue.toLocaleString()}</span>
                  </li>
                  <li className="flex justify-between">
                    <span className="text-gray-600">Total Expenditures</span>
                    <span className="font-medium">${stats.total_operating_expenditures.toLocaleString()}</span>
                  </li>
                  <li className="flex justify-between">
                    <span className="text-gray-600">Staff Expenditures</span>
                    <span className="font-medium">${stats.staff_expenditures.toLocaleString()}</span>
                  </li>
                  <li className="flex justify-between">
                    <span className="text-gray-600">Collection Expenditures</span>
                    <span className="font-medium">${stats.collection_expenditures.toLocaleString()}</span>
                  </li>
                </ul>
              </div>
            </div>
          </Card>
          
          <div className="flex justify-center">
            <Link
              to={`/historical?library=${libraryId}`}
              className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded inline-flex items-center"
            >
              <TrendingUp className="h-5 w-5 mr-2" />
              View Historical Trends
            </Link>
          </div>
        </>
      )}
    </div>
  );
};

export default LibraryDetails; 