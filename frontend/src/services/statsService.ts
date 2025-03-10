import { get } from '@/utils/api';

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
    
    return get<SummaryStats>(`/api/v1/stats/summary?${params.toString()}`);
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
    
    return get<TrendStats>(`/api/v1/stats/trends?${params.toString()}`);
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
    
    return get<ComparisonStats>(`/api/v1/stats/comparison?${params.toString()}`);
  },
  
  /**
   * Get available statistic categories and metrics
   */
  getStatisticCategories: async (): Promise<StatisticCategory[]> => {
    return get<StatisticCategory[]>('/api/v1/stats/categories');
  },
  
  /**
   * Get dashboard summary for a library
   */
  getDashboardSummary: async (
    libraryId: string = 'NY0773',
    year: number = 2006
  ): Promise<DashboardSummary> => {
    return get<DashboardSummary>(`/api/dashboard/summary?library_id=${libraryId}&year=${year}`);
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
    
    return get<KPI[]>(`/api/dashboard/kpis?${params.toString()}`);
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