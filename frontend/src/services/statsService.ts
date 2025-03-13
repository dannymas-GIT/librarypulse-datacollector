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
  description: string;
  metrics: StatisticMetric[];
}

export interface StatisticMetric {
  id: string;
  name: string;
  description: string;
  unit: string;
}

export interface KPI {
  name: string;
  value: number;
  previous_value?: number;
  change_percent?: number;
  trend?: string;
  unit?: string;
}

export interface DashboardSummary {
  library_id: string;
  library_name: string;
  year: number;
  kpis: KPI[];
}

// Stats service functions
const statsService = {
  /**
   * Get summary statistics for a specific year
   */
  getSummaryStats: async (year: number, state?: string): Promise<SummaryStats> => {
    const params = new URLSearchParams();
    params.append('year', year.toString());
    if (state) {
      params.append('state', state);
    }
    
    const endpoint = `${apiConfig.backend.endpoints.statistics}/summary?${params.toString()}`;
    return get<SummaryStats>(endpoint);
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
    
    const endpoint = `${apiConfig.backend.endpoints.statistics}/trends?${params.toString()}`;
    return get<TrendStats>(endpoint);
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
    
    const endpoint = `${apiConfig.backend.endpoints.statistics}/comparison?${params.toString()}`;
    return get<ComparisonStats>(endpoint);
  },
  
  /**
   * Get available statistic categories and metrics
   */
  getStatisticCategories: async (): Promise<StatisticCategory[]> => {
    const endpoint = `${apiConfig.backend.endpoints.statistics}/categories`;
    return get<StatisticCategory[]>(endpoint);
  },
  
  /**
   * Get dashboard summary for a library
   */
  getDashboardSummary: async (
    libraryId: string = 'NY0773',
    year: number | string = 2006
  ): Promise<DashboardSummary> => {
    try {
      // Try to get data from the API
      console.log(`Fetching dashboard data for library ${libraryId} and year ${year} from API`);
      const endpoint = `${apiConfig.backend.endpoints.dashboard}/summary?library_id=${libraryId}&year=${year}`;
      return await get<DashboardSummary>(endpoint);
    } catch (error) {
      console.log('Error fetching dashboard data, using mock data:', error);
      
      // If API fails, return mock data
      console.log(`Generating mock dashboard data for library ${libraryId} and year ${year}`);
      
      // Define library names for known libraries
      const libraryNames = {
        'NY0773': 'West Babylon Public Library',
        'NY0001': 'Amityville Public Library',
        'NY0002': 'Babylon Public Library',
        'NY0784': 'Wyandanch Public Library',
        'NY0776': 'Smithtown Library',
        'NY0788': 'Huntington Public Library',
        'NY0845': 'Patchogue-Medford Library',
        'NY0856': 'Port Jefferson Free Library'
      };
      
      // Generate random values for metrics
      const baseCirculation = 350000;
      const baseVisits = 195000;
      const basePrograms = 480;
      const baseProgramAttendance = 13500;
      const basePrintCollection = 120000;
      const baseElectronicCollection = 50000;
      
      // Use a multiplier based on the library ID to get different but consistent values
      const multiplier = parseInt(libraryId.replace(/\D/g, '')) % 10 / 10 + 0.5;
      
      return {
        library_id: libraryId,
        library_name: libraryNames[libraryId as keyof typeof libraryNames] || `Library ${libraryId}`,
        year: Number(year),
        kpis: [
          {
            name: "Total Circulation",
            value: Math.round(baseCirculation * multiplier),
            previous_value: Math.round(baseCirculation * multiplier * 0.9),
            change_percent: Math.round(10 * multiplier),
            trend: "up",
            unit: "items"
          },
          {
            name: "Visits",
            value: Math.round(baseVisits * multiplier),
            previous_value: Math.round(baseVisits * multiplier * 0.95),
            change_percent: Math.round(5 * multiplier),
            trend: "up",
            unit: "visits"
          },
          {
            name: "Total Programs",
            value: Math.round(basePrograms * multiplier),
            previous_value: Math.round(basePrograms * multiplier * 0.92),
            change_percent: Math.round(8 * multiplier),
            trend: "up",
            unit: "programs"
          },
          {
            name: "Program Attendance",
            value: Math.round(baseProgramAttendance * multiplier),
            previous_value: Math.round(baseProgramAttendance * multiplier * 0.9),
            change_percent: Math.round(10 * multiplier),
            trend: "up",
            unit: "attendees"
          },
          {
            name: "Print Collection",
            value: Math.round(basePrintCollection * multiplier),
            previous_value: Math.round(basePrintCollection * multiplier * 0.98),
            change_percent: Math.round(2 * multiplier),
            trend: "up",
            unit: "items"
          },
          {
            name: "Electronic Collection",
            value: Math.round(baseElectronicCollection * multiplier),
            previous_value: Math.round(baseElectronicCollection * multiplier * 0.85),
            change_percent: Math.round(15 * multiplier),
            trend: "up",
            unit: "items"
          }
        ]
      };
    }
  },
  
  /**
   * Get KPIs for a library
   */
  getKPIs: async (
    libraryId: string = 'NY0773',
    year: number = 2006,
    metrics: string[] = ['total_circulation', 'visits', 'total_programs', 'total_program_attendance']
  ): Promise<KPI[]> => {
    const params = new URLSearchParams();
    params.append('library_id', libraryId);
    params.append('year', year.toString());
    metrics.forEach(metric => params.append('metrics', metric));
    
    const endpoint = `${apiConfig.backend.endpoints.dashboard}/kpis?${params.toString()}`;
    return get<KPI[]>(endpoint);
  }
};

// For backward compatibility
export const fetchSummaryStats = (year?: number, state?: string): Promise<SummaryStats> => {
  return statsService.getSummaryStats(year || 2022, state);
};

export const fetchTrendStats = (
  metrics: string[],
  startYear?: number,
  endYear?: number,
  state?: string
): Promise<TrendStats> => {
  return statsService.getTrendStats(metrics, startYear || 2017, endYear || 2022, state);
};

export const fetchComparisonStats = (
  libraryIds: string[],
  year?: number,
  metrics?: string[]
): Promise<ComparisonStats> => {
  return statsService.getComparisonStats(libraryIds, year || 2022, metrics || ['total_circulation', 'visits']);
};

// Export default
export default statsService; 