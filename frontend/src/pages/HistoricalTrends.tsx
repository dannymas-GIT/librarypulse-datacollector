// @ts-nocheck
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  LineChart,
  Line
} from 'recharts';
import { AlertCircle, Calendar, BarChart as LucideBarChart } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { Card } from '@/components/ui/Card';
import { Select } from '@/components/ui/Select';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { ErrorMessage } from '@/components/ui/ErrorMessage';
import { Toggle } from '@/components/ui/Toggle';
import libraryDataService from '@/services/libraryDataService';
import statsService from '@/services/statsService';
import { ChevronDown, ChevronUp, DollarSign, TrendingDown, TrendingUp, Calculator, BookOpen, Users, FileText, PieChart, AlertTriangle, Info, Lightbulb, BookOpenCheck } from 'lucide-react';

// Define the API URL directly
const API_URL = 'http://localhost:8000/api/historical';

// Add debug logs
console.log('HistoricalTrends component loaded');
console.log('API URL:', API_URL);

// Define interfaces for the data
interface TrendData {
  metric: string;
  years: number[];
  values: (number | null)[];
  growth_rates?: {
    yearly?: Record<string, number>;
    average?: number;
    total?: number;
  };
}

interface ChartData {
  year: number;
  [key: string]: number | null | undefined;
}

type MetricOption = {
  value: string;
  label: string;
  category: string;
  color: string;
};

const METRIC_OPTIONS: MetricOption[] = [
  // Circulation metrics
  { value: 'total_circulation', label: 'Total Circulation', category: 'Circulation', color: '#8884d8' },
  { value: 'electronic_circulation', label: 'Electronic Circulation', category: 'Circulation', color: '#82ca9d' },
  { value: 'physical_circulation', label: 'Physical Circulation', category: 'Circulation', color: '#ffc658' },
  
  // Visit metrics
  { value: 'visits', label: 'Total Visits', category: 'Visits', color: '#ff8042' },
  { value: 'reference_transactions', label: 'Reference Transactions', category: 'Visits', color: '#00C49F' },
  { value: 'website_visits', label: 'Website Visits', category: 'Visits', color: '#FFBB28' },
  
  // Collection metrics
  { value: 'print_collection', label: 'Print Collection', category: 'Collections', color: '#0088FE' },
  { value: 'electronic_collection', label: 'Electronic Collection', category: 'Collections', color: '#00C49F' },
  { value: 'audio_collection', label: 'Audio Collection', category: 'Collections', color: '#FFBB28' },
  { value: 'video_collection', label: 'Video Collection', category: 'Collections', color: '#FF8042' },
  
  // Programs metrics
  { value: 'total_programs', label: 'Total Programs', category: 'Programs', color: '#0088FE' },
  { value: 'total_program_attendance', label: 'Total Program Attendance', category: 'Programs', color: '#00C49F' },
  { value: 'children_programs', label: 'Children Programs', category: 'Programs', color: '#FFBB28' },
  { value: 'children_program_attendance', label: 'Children Program Attendance', category: 'Programs', color: '#FF8042' },
  { value: 'adult_programs', label: 'Adult Programs', category: 'Programs', color: '#83a6ed' },
  { value: 'adult_program_attendance', label: 'Adult Program Attendance', category: 'Programs', color: '#8dd1e1' },
  
  // Financial metrics
  { value: 'total_operating_revenue', label: 'Total Revenue', category: 'Financial', color: '#a4de6c' },
  { value: 'total_operating_expenditures', label: 'Total Expenditures', category: 'Financial', color: '#d0ed57' },
  { value: 'staff_expenditures', label: 'Staff Expenditures', category: 'Financial', color: '#ffc658' },
  { value: 'collection_expenditures', label: 'Collection Expenditures', category: 'Financial', color: '#8884d8' }
];

// Group metric options by category
const groupedMetrics = METRIC_OPTIONS.reduce<Record<string, MetricOption[]>>((acc, metric) => {
  if (!acc[metric.category]) {
    acc[metric.category] = [];
  }
  acc[metric.category].push(metric);
  return acc;
}, {});

const HistoricalTrends: React.FC = () => {
  const [selectedMetrics, setSelectedMetrics] = useState<string[]>(['total_circulation', 'electronic_circulation', 'physical_circulation']);
  const [chartType, setChartType] = useState<'line' | 'bar'>('line');
  const [yearRange, setYearRange] = useState<[number, number]>([1988, 2024]);
  const [trendData, setTrendData] = useState<TrendData[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [availableYears, setAvailableYears] = useState<number[]>([]);
  
  // Add the missing selectedLibrary state
  const [selectedLibrary, setSelectedLibrary] = useState({
    id: 'NY0773',
    name: 'West Babylon Public Library'
  });
  
  // Get user preferences to set the selected library
  useEffect(() => {
    const getUserPreferences = async () => {
      try {
        const preferences = await libraryDataService.getUserPreferences();
        if (preferences && preferences.primaryLibraryId) {
          setSelectedLibrary({
            id: preferences.primaryLibraryId,
            name: preferences.primaryLibraryId === 'NY0773' 
              ? 'West Babylon Public Library' 
              : preferences.primaryLibraryId === 'NY0001'
                ? 'Amityville Public Library'
                : preferences.primaryLibraryId === 'NY0002'
                  ? 'Babylon Public Library'
                  : `Library ${preferences.primaryLibraryId}`
          });
        }
      } catch (error) {
        console.error('Error fetching user preferences:', error);
      }
    };
    
    getUserPreferences();
  }, []);
  
  // Fetch available years
  useEffect(() => {
    const fetchYears = async () => {
      console.log('Fetching years from:', `${API_URL}/years`);
      try {
        const response = await fetch(`${API_URL}/years`);
        console.log('Years response status:', response.status);
        const data = await response.json();
        console.log('Years data:', data);
        setAvailableYears(data);
        
        // Update year range based on available years
        if (data && data.length > 0) {
          const minYear = Math.min(...data);
          const maxYear = Math.max(...data);
          setYearRange([minYear, maxYear]);
        }
      } catch (error) {
        console.error('Error fetching years:', error);
      }
    };
    
    fetchYears();
  }, []);
  
  // Fetch trend data when selected metrics change
  useEffect(() => {
    const fetchTrendData = async () => {
      if (selectedMetrics.length === 0) return;
      
      setLoading(true);
      setError(null);
      
      try {
        // Construct the URL with query parameters
        const params = new URLSearchParams();
        selectedMetrics.forEach(metric => params.append('metrics', metric));
        params.append('start_year', yearRange[0].toString());
        params.append('end_year', yearRange[1].toString());
        
        const url = `${API_URL}/trends?${params.toString()}`;
        
        console.log('Fetching trend data from:', url);
        const response = await fetch(url);
        console.log('Trend data response status:', response.status);
        const data = await response.json();
        console.log('Trend data response:', data);
        
        setTrendData(data);
      } catch (error) {
        console.error('Error fetching trend data:', error);
        setError(String(error));
      } finally {
        setLoading(false);
      }
    };
    
    fetchTrendData();
  }, [selectedMetrics, yearRange]);
  
  // Process data for chart
  const processChartData = (): ChartData[] => {
    if (!trendData || trendData.length === 0) return [];

    // Get all years from all metrics
    const allYears = new Set<number>();
    trendData.forEach((metric) => {
      metric.years.forEach((year) => allYears.add(year));
    });

    // Filter years based on year range
    const filteredYears = Array.from(allYears)
      .filter(year => year >= yearRange[0] && year <= yearRange[1])
      .sort((a, b) => a - b);

    // Create chart data
    return filteredYears.map(year => {
      const dataPoint: ChartData = { year };
      
      trendData.forEach(metric => {
        const yearIndex = metric.years.indexOf(year);
        if (yearIndex !== -1) {
          dataPoint[metric.metric] = metric.values[yearIndex];
        } else {
          dataPoint[metric.metric] = null;
        }
      });
      
      return dataPoint;
    });
  };

  // Handle metric selection
  const handleMetricChange = (metric: string) => {
    setSelectedMetrics(prev => {
      if (prev.includes(metric)) {
        return prev.filter(m => m !== metric);
      } else {
        return [...prev, metric];
      }
    });
  };

  // Generate chart based on processed data
  const renderChart = () => {
    const chartData = processChartData();
    const selectedMetricOptions = METRIC_OPTIONS.filter(option => 
      selectedMetrics.includes(option.value)
    );

    if (chartType === 'line') {
      return (
        <ResponsiveContainer width="100%" height={500}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="year" />
            <YAxis />
            <Tooltip 
              formatter={(value: any, name: any) => {
                const metricOption = METRIC_OPTIONS.find(m => m.value === name);
                return [value, metricOption?.label || name];
              }}
            />
            <Legend />
            {selectedMetricOptions.map(metric => (
              <Line
                key={metric.value}
                type="monotone"
                dataKey={metric.value}
                name={metric.label}
                stroke={metric.color}
                activeDot={{ r: 8 }}
                connectNulls
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      );
    } else {
      return (
        <ResponsiveContainer width="100%" height={500}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="year" />
            <YAxis />
            <Tooltip 
              formatter={(value: any, name: any) => {
                const metricOption = METRIC_OPTIONS.find(m => m.value === name);
                return [value, metricOption?.label || name];
              }}
            />
            <Legend />
            {selectedMetricOptions.map(metric => (
              <Bar
                key={metric.value}
                dataKey={metric.value}
                name={metric.label}
                fill={metric.color}
              />
            ))}
          </BarChart>
        </ResponsiveContainer>
      );
    }
  };

  // Show loading state
  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center">
        <div className="animate-spin w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full"></div>
        <span className="ml-4 text-lg font-medium">Loading historical data...</span>
      </div>
    );
  }

  // Show error state
  if (error) {
    return (
      <div className="h-screen flex items-center justify-center text-red-500">
        <div className="w-10 h-10 text-red-500">⚠️</div>
        <span className="ml-4 text-lg font-medium">
          Error loading historical data: {error}
        </span>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-4">
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <h1 className="text-2xl font-bold mb-6">West Babylon Public Library Historical Trends</h1>
        
        {/* Chart controls */}
        <div className="mb-6 flex flex-wrap gap-4">
          <div className="flex items-center space-x-4">
            <button
              className={`px-4 py-2 rounded-md flex items-center ${
                chartType === 'line' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-800'
              }`}
              onClick={() => setChartType('line')}
            >
              <span className="mr-2">📈</span>
              Line Chart
            </button>
            <button
              className={`px-4 py-2 rounded-md flex items-center ${
                chartType === 'bar' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-800'
              }`}
              onClick={() => setChartType('bar')}
            >
              <span className="mr-2">📊</span>
              Bar Chart
            </button>
          </div>

          <div className="flex items-center space-x-2">
            <span className="mr-2">📅</span>
            <span className="font-medium">Year Range:</span>
            <input 
              type="number" 
              min={1988} 
              max={2024}
              value={yearRange[0]} 
              onChange={(e) => setYearRange([parseInt(e.target.value), yearRange[1]])}
              className="border rounded px-2 py-1 w-20"
            />
            <span>to</span>
            <input 
              type="number" 
              min={1988} 
              max={2024}
              value={yearRange[1]} 
              onChange={(e) => setYearRange([yearRange[0], parseInt(e.target.value)])}
              className="border rounded px-2 py-1 w-20"
            />
          </div>
        </div>

        {/* Metrics selection */}
        <div className="mb-8">
          <h2 className="text-lg font-semibold mb-3">Select Metrics to Display</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(groupedMetrics).map(([category, metrics]) => (
              <div key={category} className="bg-gray-50 p-4 rounded-lg">
                <h3 className="font-medium text-gray-700 mb-2">{category}</h3>
                <div className="space-y-2">
                  {metrics.map((metric) => (
                    <div key={metric.value} className="flex items-center">
                      <input
                        type="checkbox"
                        id={metric.value}
                        checked={selectedMetrics.includes(metric.value)}
                        onChange={() => handleMetricChange(metric.value)}
                        className="mr-2 h-4 w-4 text-blue-600 focus:ring-blue-500 rounded"
                      />
                      <label htmlFor={metric.value} className="text-sm">
                        {metric.label}
                      </label>
                      <div 
                        className="w-3 h-3 rounded-full ml-2" 
                        style={{ backgroundColor: metric.color }}
                      />
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Chart */}
        <div className="bg-white p-4 rounded-lg border">
          {selectedMetrics.length > 0 ? (
            renderChart()
          ) : (
            <div className="h-64 flex items-center justify-center text-gray-500">
              <span>Select at least one metric to display the chart</span>
            </div>
          )}
        </div>

        {/* Growth rates information */}
        {trendData && trendData.length > 0 && (
          <div className="mt-8">
            <h2 className="text-lg font-semibold mb-3">Growth Analysis</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {trendData.map((trend) => {
                const metricOption = METRIC_OPTIONS.find(m => m.value === trend.metric);
                const hasGrowthData = trend.growth_rates && trend.growth_rates.total;
                
                return (
                  <div key={trend.metric} className="bg-gray-50 p-4 rounded-lg">
                    <h3 className="font-medium text-gray-700 mb-2">
                      {metricOption?.label || trend.metric}
                    </h3>
                    {hasGrowthData ? (
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span>Total Growth:</span>
                          <span className={trend.growth_rates?.total && trend.growth_rates.total > 0 ? 'text-green-600' : 'text-red-600'}>
                            {trend.growth_rates?.total ? `${trend.growth_rates.total.toFixed(2)}%` : 'N/A'}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span>Avg. Annual Growth:</span>
                          <span className={trend.growth_rates?.average && trend.growth_rates.average > 0 ? 'text-green-600' : 'text-red-600'}>
                            {trend.growth_rates?.average ? `${trend.growth_rates.average.toFixed(2)}%` : 'N/A'}
                          </span>
                        </div>
                        {trend.growth_rates?.yearly && Object.keys(trend.growth_rates.yearly).length > 0 && (
                          <div>
                            <div className="font-medium mt-2 mb-1">Significant Years:</div>
                            {Object.entries(trend.growth_rates.yearly)
                              .sort(([, a], [, b]) => Math.abs(Number(b)) - Math.abs(Number(a)))
                              .slice(0, 3)
                              .map(([year, rate]) => (
                                <div key={year} className="flex justify-between">
                                  <span>{year}:</span>
                                  <span className={Number(rate) > 0 ? 'text-green-600' : 'text-red-600'}>
                                    {typeof rate === 'number' ? `${rate.toFixed(2)}%` : 'N/A'}
                                  </span>
                                </div>
                              ))}
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="text-gray-500 text-sm">No growth data available</div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Budget Forecast Section for Library Directors */}
        <div className="mb-8">
          <h2 className="text-xl font-bold mb-4 flex items-center">
            <DollarSign className="mr-2" />
            Financial Planning Tools
          </h2>
          
          <BudgetForecast 
            historicalData={trendData} 
            selectedLibrary={selectedLibrary} 
          />
        </div>
      </div>
    </div>
  );
};

// Budget Forecast component for financial projections
const BudgetForecast = ({ historicalData, selectedLibrary }) => {
  const [forecastLength, setForecastLength] = useState(3); // Years to forecast
  const [growthAssumption, setGrowthAssumption] = useState('moderate');
  
  // Growth rate assumptions for different scenarios
  const growthRates = {
    conservative: {
      revenue: 0.02, // 2% annual growth
      expenditure: 0.03 // 3% annual growth
    },
    moderate: {
      revenue: 0.03, // 3% annual growth
      expenditure: 0.035 // 3.5% annual growth
    },
    optimistic: {
      revenue: 0.045, // 4.5% annual growth
      expenditure: 0.04 // 4% annual growth
    }
  };
  
  // Get the last 5 years of financial data
  const financialHistory = historicalData?.filter(item => 
    item.metric === 'total_operating_revenue' || 
    item.metric === 'total_operating_expenditures'
  ) || [];
  
  // Group by year
  const groupedByYear = financialHistory.reduce((acc, item) => {
    if (!acc[item.year]) {
      acc[item.year] = {};
    }
    acc[item.year][item.metric] = item.value;
    return acc;
  }, {});
  
  // Convert to array for chart
  const financialData = Object.keys(groupedByYear).map(year => ({
    year: parseInt(year),
    revenue: groupedByYear[year].total_operating_revenue || 0,
    expenditure: groupedByYear[year].total_operating_expenditures || 0
  })).sort((a, b) => a.year - b.year);
  
  // Generate forecast data
  const generateForecast = () => {
    if (financialData.length === 0) return [];
    
    const lastYear = financialData[financialData.length - 1];
    const rates = growthRates[growthAssumption];
    
    const forecast = [lastYear];
    let lastRevenue = lastYear.revenue;
    let lastExpenditure = lastYear.expenditure;
    
    for (let i = 1; i <= forecastLength; i++) {
      const year = lastYear.year + i;
      const revenue = Math.round(lastRevenue * (1 + rates.revenue));
      const expenditure = Math.round(lastExpenditure * (1 + rates.expenditure));
      
      forecast.push({ year, revenue, expenditure });
      lastRevenue = revenue;
      lastExpenditure = expenditure;
    }
    
    return forecast;
  };
  
  const forecastData = generateForecast();
  
  // Calculate key metrics
  const calculateMetrics = () => {
    if (forecastData.length <= 1) return null;
    
    const startYear = forecastData[0];
    const endYear = forecastData[forecastData.length - 1];
    
    const revenueGrowth = (endYear.revenue - startYear.revenue) / startYear.revenue;
    const expenditureGrowth = (endYear.expenditure - startYear.expenditure) / startYear.expenditure;
    const surplusDeficitStart = startYear.revenue - startYear.expenditure;
    const surplusDeficitEnd = endYear.revenue - endYear.expenditure;
    const surplusDeficitChange = surplusDeficitEnd - surplusDeficitStart;
    
    return {
      revenueGrowth,
      expenditureGrowth,
      surplusDeficitStart,
      surplusDeficitEnd,
      surplusDeficitChange
    };
  };
  
  const metrics = calculateMetrics();
  
  // Generate budget recommendations
  const generateRecommendations = () => {
    if (!metrics) return [];
    
    const recommendations = [];
    
    // Recommendation based on surplus/deficit
    if (metrics.surplusDeficitEnd < 0) {
      recommendations.push({
        title: 'Address Budget Deficit',
        description: `Projected deficit of $${Math.abs(metrics.surplusDeficitEnd).toLocaleString()} by year ${forecastData[forecastData.length - 1].year}`,
        icon: <AlertTriangle className="text-red-500" />,
        actions: [
          'Identify potential new revenue sources',
          'Review discretionary spending',
          'Consider phased implementation of new initiatives'
        ]
      });
    }
    
    // Recommendation based on revenue vs expenditure growth
    if (metrics.revenueGrowth < metrics.expenditureGrowth) {
      recommendations.push({
        title: 'Expense Growth Outpacing Revenue',
        description: 'Expenditures are growing faster than revenue, which may lead to future budget constraints',
        icon: <TrendingUp className="text-amber-500" />,
        actions: [
          'Develop cost containment strategies',
          'Explore grant opportunities',
          'Consider service efficiency improvements'
        ]
      });
    }
    
    // Recommendation for healthy budget
    if (metrics.surplusDeficitEnd > 0 && metrics.revenueGrowth >= metrics.expenditureGrowth) {
      recommendations.push({
        title: 'Reinvestment Opportunity',
        description: `Projected surplus of $${metrics.surplusDeficitEnd.toLocaleString()} provides opportunity for strategic investments`,
        icon: <Lightbulb className="text-green-500" />,
        actions: [
          'Prioritize facility improvements',
          'Invest in technology infrastructure',
          'Expand high-demand collections or services'
        ]
      });
    }
    
    // If expenditure is rising substantially
    if (metrics.expenditureGrowth > 0.15) {
      recommendations.push({
        title: 'Significant Expenditure Growth',
        description: `${(metrics.expenditureGrowth * 100).toFixed(1)}% projected growth in expenses over ${forecastLength} years may require budget restructuring`,
        icon: <Info className="text-blue-500" />,
        actions: [
          'Conduct line-item budget review',
          'Develop multi-year phasing for major expenses',
          'Explore cooperative purchasing opportunities'
        ]
      });
    }
    
    return recommendations;
  };
  
  const recommendations = generateRecommendations();
  
  return (
    <Card className="p-4 lg:p-6">
      <div className="flex flex-col lg:flex-row justify-between mb-4">
        <div>
          <h2 className="text-xl font-semibold flex items-center">
            <Calculator className="w-5 h-5 mr-2 text-blue-500" />
            Budget Forecast
          </h2>
          <p className="text-gray-600 text-sm mt-1">
            Financial projections based on historical trends to assist with budget planning
          </p>
        </div>
        
        <div className="flex items-center space-x-4 mt-4 lg:mt-0">
          <div>
            <label className="block text-sm text-gray-700 mb-1">Forecast Years</label>
            <Select
              value={forecastLength.toString()}
              onChange={e => setForecastLength(parseInt(e.target.value))}
              options={[
                { value: '2', label: '2 Years' },
                { value: '3', label: '3 Years' },
                { value: '5', label: '5 Years' }
              ]}
              className="w-32"
            />
          </div>
          
          <div>
            <label className="block text-sm text-gray-700 mb-1">Growth Scenario</label>
            <Select
              value={growthAssumption}
              onChange={e => setGrowthAssumption(e.target.value)}
              options={[
                { value: 'conservative', label: 'Conservative' },
                { value: 'moderate', label: 'Moderate' },
                { value: 'optimistic', label: 'Optimistic' }
              ]}
              className="w-36"
            />
          </div>
        </div>
      </div>
      
      {/* Forecast Chart */}
      <div className="h-80 mt-6">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={forecastData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <defs>
              <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#8884d8" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#8884d8" stopOpacity={0.1}/>
              </linearGradient>
              <linearGradient id="colorExpenditure" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#82ca9d" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#82ca9d" stopOpacity={0.1}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="year" />
            <YAxis tickFormatter={(value) => `$${value / 1000}k`} />
            <Tooltip 
              formatter={(value) => [`$${value.toLocaleString()}`, undefined]}
              labelFormatter={(label) => `Year: ${label}`}
            />
            <Legend />
            <Area 
              type="monotone" 
              dataKey="revenue" 
              name="Revenue" 
              stroke="#8884d8" 
              fillOpacity={1} 
              fill="url(#colorRevenue)" 
            />
            <Area 
              type="monotone" 
              dataKey="expenditure" 
              name="Expenditure" 
              stroke="#82ca9d" 
              fillOpacity={1} 
              fill="url(#colorExpenditure)" 
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
      
      {/* Forecast Metrics */}
      {metrics && (
        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
            <h3 className="text-blue-800 font-medium mb-1">Revenue Growth</h3>
            <div className="text-2xl font-bold text-blue-900">{(metrics.revenueGrowth * 100).toFixed(1)}%</div>
            <p className="text-blue-600 text-sm">Over {forecastLength} years</p>
          </div>
          
          <div className="bg-green-50 p-4 rounded-lg border border-green-200">
            <h3 className="text-green-800 font-medium mb-1">Expenditure Growth</h3>
            <div className="text-2xl font-bold text-green-900">{(metrics.expenditureGrowth * 100).toFixed(1)}%</div>
            <p className="text-green-600 text-sm">Over {forecastLength} years</p>
          </div>
          
          <div className={`p-4 rounded-lg border ${metrics.surplusDeficitEnd >= 0 ? 'bg-emerald-50 border-emerald-200' : 'bg-red-50 border-red-200'}`}>
            <h3 className={`font-medium mb-1 ${metrics.surplusDeficitEnd >= 0 ? 'text-emerald-800' : 'text-red-800'}`}>
              Projected {metrics.surplusDeficitEnd >= 0 ? 'Surplus' : 'Deficit'}
            </h3>
            <div className={`text-2xl font-bold ${metrics.surplusDeficitEnd >= 0 ? 'text-emerald-900' : 'text-red-900'}`}>
              ${Math.abs(metrics.surplusDeficitEnd).toLocaleString()}
            </div>
            <p className={`text-sm ${metrics.surplusDeficitEnd >= 0 ? 'text-emerald-600' : 'text-red-600'}`}>
              By {forecastData[forecastData.length - 1].year}
            </p>
          </div>
        </div>
      )}
      
      {/* Budget Recommendations */}
      {recommendations.length > 0 && (
        <div className="mt-8">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <Lightbulb className="w-5 h-5 mr-2 text-amber-500" />
            Budget Planning Recommendations
          </h3>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {recommendations.map((rec, idx) => (
              <div key={idx} className="border rounded-lg p-4 bg-gray-50">
                <div className="flex items-start">
                  <div className="mr-3 mt-1">{rec.icon}</div>
                  <div>
                    <h4 className="font-medium text-gray-900">{rec.title}</h4>
                    <p className="text-gray-700 text-sm mb-3">{rec.description}</p>
                    
                    <h5 className="text-sm font-medium text-gray-800 mb-1">Suggested Actions:</h5>
                    <ul className="text-sm space-y-1">
                      {rec.actions.map((action, actionIdx) => (
                        <li key={actionIdx} className="flex items-start">
                          <span className="text-blue-500 mr-2">•</span>
                          <span>{action}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      <div className="mt-6 text-sm text-gray-500 border-t pt-4">
        <div className="flex items-center">
          <Info className="w-4 h-4 mr-1 text-blue-500" />
          <span>This forecast is based on historical data and selected growth assumptions. Actual results may vary.</span>
        </div>
      </div>
    </Card>
  );
};

export default HistoricalTrends;

// Re-export from Lucide
const Chart = LucideBarChart; 