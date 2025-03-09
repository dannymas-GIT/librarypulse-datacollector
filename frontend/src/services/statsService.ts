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
}

export interface StatisticMetric {
  id: string;
  name: string;
  description: string;
  category: string;
  unit: string;
  dataType: 'number' | 'percentage' | 'currency' | 'text';
}

export interface StatisticValue {
  metric: string;
  value: number | string;
  year: number;
}

export interface LibraryStatistics {
  libraryId: number;
  libraryName: string;
  fscsId: string;
  year: number;
  statistics: StatisticValue[];
}

export interface TrendPoint {
  year: number;
  value: number | string;
}

export interface TrendData {
  metric: StatisticMetric;
  data: TrendPoint[];
}

export interface ComparisonData {
  metric: StatisticMetric;
  libraries: {
    id: number;
    name: string;
    value: number | string;
  }[];
}

export interface StateAverage {
  state: string;
  metric: string;
  value: number;
  year: number;
}

export interface NationalAverage {
  metric: string;
  value: number;
  year: number;
}

// Updated API functions using the new api utility
export const fetchSummaryStats = (year?: number, state?: string): Promise<SummaryStats> => {
  const params: Record<string, any> = {};
  if (year) params.year = year;
  if (state) params.state = state;

  return get<SummaryStats>('/stats/summary', params);
};

export const fetchTrendStats = (
  metrics: string[],
  startYear?: number,
  endYear?: number,
  state?: string
): Promise<TrendStats> => {
  const params: Record<string, any> = {
    metrics: metrics.join(',')
  };
  if (startYear) params.start_year = startYear;
  if (endYear) params.end_year = endYear;
  if (state) params.state = state;

  return get<TrendStats>('/stats/trends', params);
};

export const fetchComparisonStats = (
  libraryIds: string[],
  year?: number,
  metrics?: string[]
): Promise<ComparisonStats> => {
  const params: Record<string, any> = {
    library_ids: libraryIds.join(',')
  };
  if (year) params.year = year;
  if (metrics) params.metrics = metrics.join(',');

  return get<ComparisonStats>('/stats/comparison', params);
};

// Get all statistic categories
export const getStatisticCategories = (): Promise<StatisticCategory[]> => {
  return get<StatisticCategory[]>('/statistics/categories');
};

// Get all metrics
export const getStatisticMetrics = (categoryId?: string): Promise<StatisticMetric[]> => {
  const params = categoryId ? { category: categoryId } : {};
  return get<StatisticMetric[]>('/statistics/metrics', params);
};

// Get statistics for a specific library
export const getLibraryStatistics = (
  libraryId: number,
  year?: number,
  categoryId?: string
): Promise<LibraryStatistics> => {
  const params = {
    ...(year && { year }),
    ...(categoryId && { category: categoryId }),
  };
  return get<LibraryStatistics>(`/libraries/${libraryId}/statistics`, params);
};

// Get trend data for a specific metric and library
export const getLibraryTrend = (
  libraryId: number,
  metricId: string,
  startYear?: number,
  endYear?: number
): Promise<TrendData> => {
  const params = {
    ...(startYear && { start_year: startYear }),
    ...(endYear && { end_year: endYear }),
  };
  return get<TrendData>(`/libraries/${libraryId}/trends/${metricId}`, params);
};

// Get multiple trends for a library
export const getLibraryTrends = (
  libraryId: number,
  metricIds: string[],
  startYear?: number,
  endYear?: number
): Promise<TrendData[]> => {
  const params = {
    metrics: metricIds.join(','),
    ...(startYear && { start_year: startYear }),
    ...(endYear && { end_year: endYear }),
  };
  return get<TrendData[]>(`/libraries/${libraryId}/trends`, params);
};

// Compare libraries for a specific metric
export const compareLibraries = (
  libraryIds: number[],
  metricId: string,
  year?: number
): Promise<ComparisonData> => {
  const params = {
    libraries: libraryIds.join(','),
    ...(year && { year }),
  };
  return get<ComparisonData>(`/statistics/compare/${metricId}`, params);
};

// Compare libraries for multiple metrics
export const compareLibrariesMultiMetric = (
  libraryIds: number[],
  metricIds: string[],
  year?: number
): Promise<ComparisonData[]> => {
  const params = {
    libraries: libraryIds.join(','),
    metrics: metricIds.join(','),
    ...(year && { year }),
  };
  return get<ComparisonData[]>('/statistics/compare', params);
};

// Get state averages for a metric
export const getStateAverages = (
  metricId: string,
  year?: number
): Promise<StateAverage[]> => {
  const params = year ? { year } : {};
  return get<StateAverage[]>(`/statistics/state-averages/${metricId}`, params);
};

// Get national average for a metric
export const getNationalAverage = (
  metricId: string,
  year?: number
): Promise<NationalAverage> => {
  const params = year ? { year } : {};
  return get<NationalAverage>(`/statistics/national-average/${metricId}`, params);
};

// Get available years for statistics
export const getAvailableYears = (): Promise<number[]> => {
  return get<number[]>('/statistics/years');
}; 