import { get } from '@/utils/api';
import { apiConfig } from '@/config/api';

// Define types for API responses
export interface SummaryStats {
  year: number;
  state?: string;
  library_count: number;
  total_visits: number;
  total_circulation: number;
  total_programs: number;
  total_program_attendance: number;
  total_operating_revenue: number;
  total_operating_expenditures: number;
  total_staff: number;
  outlet_count: number;
  avg_visits_per_library?: number;
  avg_circulation_per_library?: number;
  avg_programs_per_library?: number;
  avg_operating_revenue_per_library?: number;
  avg_operating_expenditures_per_library?: number;
  avg_staff_per_library?: number;
}

export interface TrendStats {
  years: number[];
  [metric: string]: number[] | number;
}

export interface ComparisonStats {
  year: number;
  libraries: {
    library_id: string;
    name: string;
    state: string;
    metrics: {
      [key: string]: {
        name: string;
        value: number;
      };
    };
  }[];
  metric_definitions: {
    [key: string]: string;
  };
}

export interface StatisticCategory {
  id: string;
  name: string;
  metrics: {
    id: string;
    name: string;
    description?: string;
  }[];
}

export interface KPI {
  name: string;
  value: number;
  previous_value?: number;
  change_percent?: number;
  trend?: 'up' | 'down' | 'stable';
  unit?: string;
}

export interface DashboardSummary {
  library_id: string;
  library_name: string;
  year: number;
  kpis: KPI[];
}

// Stats service functions
export const statsService = {
  /**
   * Get summary statistics for a specific year
   */
  getSummaryStats: async (year: number, state?: string): Promise<SummaryStats> => {
    const params = new URLSearchParams();
    params.append('year', year.toString());
    if (state) {
      params.append('state', state);
    }
    
    try {
      const endpoint = `${apiConfig.backend.endpoints.statistics}/summary?${params.toString()}`;
      console.log('Fetching summary stats with URL:', endpoint);
      return await get<SummaryStats>(endpoint);
    } catch (error) {
      console.error('Error fetching summary stats:', error);
      
      // Return mock data as fallback
      return {
        year,
        state: state || 'NY',
        library_count: 44,
        total_visits: 1250000,
        total_circulation: 2500000,
        total_programs: 3500,
        total_program_attendance: 75000,
        total_operating_revenue: 15000000,
        total_operating_expenditures: 14000000,
        total_staff: 350,
        outlet_count: 50,
        avg_visits_per_library: 28409,
        avg_circulation_per_library: 56818,
        avg_programs_per_library: 79.5,
        avg_operating_revenue_per_library: 340909,
        avg_operating_expenditures_per_library: 318182,
        avg_staff_per_library: 7.95
      };
    }
  },
  
  /**
   * Get trend statistics for a range of years
   */
  getTrendStats: async (
    metrics: string[],
    startYear: number,
    endYear: number,
    state?: string
  ): Promise<TrendStats> => {
    const params = new URLSearchParams();
    metrics.forEach(metric => params.append('metrics', metric));
    params.append('start_year', startYear.toString());
    params.append('end_year', endYear.toString());
    if (state) {
      params.append('state', state);
    }
    
    try {
      const endpoint = `${apiConfig.backend.endpoints.statistics}/trends?${params.toString()}`;
      console.log('Fetching trend stats with URL:', endpoint);
      return await get<TrendStats>(endpoint);
    } catch (error) {
      console.error('Error fetching trend stats:', error);
      
      // Return mock data as fallback
      const years = Array.from({ length: endYear - startYear + 1 }, (_, i) => startYear + i);
      const mockTrends: TrendStats = { years };
      
      metrics.forEach(metric => {
        mockTrends[metric] = years.map(() => Math.floor(Math.random() * 1000000) + 500000);
      });
      
      return mockTrends;
    }
  },
  
  /**
   * Get comparison statistics for multiple libraries
   */
  getComparisonStats: async (
    libraryIds: string[],
    year: number,
    metrics: string[]
  ): Promise<ComparisonStats> => {
    const params = new URLSearchParams();
    libraryIds.forEach(id => params.append('library_ids', id));
    params.append('year', year.toString());
    metrics.forEach(metric => params.append('metrics', metric));
    
    try {
      const endpoint = `${apiConfig.backend.endpoints.statistics}/comparison?${params.toString()}`;
      console.log('Fetching comparison stats with URL:', endpoint);
      return await get<ComparisonStats>(endpoint);
    } catch (error) {
      console.error('Error fetching comparison stats:', error);
      
      // Return mock data as fallback
      const mockComparison: ComparisonStats = {
        year,
        libraries: libraryIds.map(id => ({
          library_id: id,
          name: id === 'NY0773' ? 'West Babylon Public Library' : 
                id === 'NY0001' ? 'Amityville Public Library' : 
                id === 'NY0002' ? 'Babylon Public Library' : `Library ${id}`,
          state: 'NY',
          metrics: metrics.reduce((acc, metric) => {
            acc[metric] = {
              name: metric.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
              value: Math.floor(Math.random() * 1000000) + 10000
            };
            return acc;
          }, {} as Record<string, { name: string; value: number }>)
        })),
        metric_definitions: metrics.reduce((acc, metric) => {
          acc[metric] = `Definition for ${metric.replace(/_/g, ' ')}`;
          return acc;
        }, {} as Record<string, string>)
      };
      
      return mockComparison;
    }
  },
  
  /**
   * Get available statistic categories and metrics
   */
  getStatisticCategories: async (): Promise<StatisticCategory[]> => {
    try {
      const endpoint = `${apiConfig.backend.endpoints.statistics}/categories`;
      console.log('Fetching statistic categories with URL:', endpoint);
      return await get<StatisticCategory[]>(endpoint);
    } catch (error) {
      console.error('Error fetching statistic categories:', error);
      
      // Return mock data as fallback
      return [
        {
          id: 'usage',
          name: 'Library Usage',
          metrics: [
            { id: 'total_circulation', name: 'Total Circulation' },
            { id: 'visits', name: 'Visits' },
            { id: 'reference_transactions', name: 'Reference Transactions' },
            { id: 'registered_users', name: 'Registered Users' }
          ]
        },
        {
          id: 'collections',
          name: 'Collections',
          metrics: [
            { id: 'print_collection', name: 'Print Collection' },
            { id: 'electronic_collection', name: 'Electronic Collection' },
            { id: 'audio_collection', name: 'Audio Collection' },
            { id: 'video_collection', name: 'Video Collection' }
          ]
        },
        {
          id: 'programs',
          name: 'Programs',
          metrics: [
            { id: 'total_programs', name: 'Total Programs' },
            { id: 'total_program_attendance', name: 'Program Attendance' },
            { id: 'children_programs', name: 'Children\'s Programs' },
            { id: 'adult_programs', name: 'Adult Programs' }
          ]
        },
        {
          id: 'finance',
          name: 'Finance',
          metrics: [
            { id: 'total_operating_revenue', name: 'Total Revenue' },
            { id: 'total_operating_expenditures', name: 'Total Expenditures' },
            { id: 'staff_expenditures', name: 'Staff Expenditures' },
            { id: 'collection_expenditures', name: 'Collection Expenditures' }
          ]
        }
      ];
    }
  },
  
  /**
   * Get KPIs for the dashboard
   */
  getKPIs: async (libraryId: string, year?: number): Promise<DashboardSummary> => {
    const params = new URLSearchParams();
    params.append('library_id', libraryId);
    if (year) {
      params.append('year', year.toString());
    }
    
    try {
      const endpoint = `${apiConfig.backend.endpoints.dashboard}/kpis?${params.toString()}`;
      console.log('Fetching KPIs with URL:', endpoint);
      return await get<DashboardSummary>(endpoint);
    } catch (error) {
      console.error('Error fetching KPIs:', error);
      
      // Generate a multiplier based on the library ID to make the mock data different for each library
      const idNum = parseInt(libraryId.replace(/\D/g, '')) || 1;
      const multiplier = (idNum % 10) / 10 + 0.5; // Between 0.5 and 1.4
      
      // Return mock data as fallback
      const libraryName = libraryId === 'NY0773' 
        ? 'West Babylon Public Library'
        : libraryId === 'NY0001'
          ? 'Amityville Public Library' 
          : libraryId === 'NY0002'
            ? 'Babylon Public Library'
            : `Library ${libraryId}`;
      
      return {
        library_id: libraryId,
        library_name: libraryName,
        year: year || 2022,
        kpis: [
          {
            name: 'Total Circulation',
            value: Math.round(250000 * multiplier),
            previous_value: Math.round(240000 * multiplier),
            change_percent: 4.2,
            trend: 'up',
            unit: 'items'
          },
          {
            name: 'Visits',
            value: Math.round(120000 * multiplier),
            previous_value: Math.round(115000 * multiplier),
            change_percent: 4.3,
            trend: 'up',
            unit: 'visits'
          },
          {
            name: 'Total Programs',
            value: Math.round(520 * multiplier),
            previous_value: Math.round(480 * multiplier),
            change_percent: 8.3,
            trend: 'up',
            unit: 'programs'
          },
          {
            name: 'Program Attendance',
            value: Math.round(12500 * multiplier),
            previous_value: Math.round(11000 * multiplier),
            change_percent: 13.6,
            trend: 'up',
            unit: 'attendees'
          },
          {
            name: 'Print Collection',
            value: Math.round(85000 * multiplier),
            previous_value: Math.round(82000 * multiplier),
            change_percent: 3.7,
            trend: 'up',
            unit: 'items'
          },
          {
            name: 'Electronic Collection',
            value: Math.round(25000 * multiplier),
            previous_value: Math.round(20000 * multiplier),
            change_percent: 25.0,
            trend: 'up',
            unit: 'items'
          }
        ]
      };
    }
  },
  
  // Mock data generators for testing
  getMockSummaryStats: (year: number, state?: string): SummaryStats => {
    return statsService.getSummaryStats(year || 2022, state);
  },
  
  getMockTrendStats: (metrics: string[], startYear?: number, endYear?: number, state?: string): TrendStats => {
    return statsService.getTrendStats(metrics, startYear || 2017, endYear || 2022, state);
  },
  
  getMockComparisonStats: (libraryIds: string[], year?: number, metrics?: string[]): ComparisonStats => {
    return statsService.getComparisonStats(libraryIds, year || 2022, metrics || ['total_circulation', 'visits']);
  }
};

export default statsService; 