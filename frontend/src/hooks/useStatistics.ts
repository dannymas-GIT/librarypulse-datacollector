import { useQuery } from '@tanstack/react-query';
import { fetchSummaryStats, fetchTrendStats, fetchComparisonStats } from '@/services/statsService';

export function useSummaryStats(year?: number, state?: string) {
  return useQuery({
    queryKey: ['summaryStats', year, state],
    queryFn: () => fetchSummaryStats(year, state),
  });
}

export function useTrendStats(
  metrics: string[],
  startYear?: number,
  endYear?: number,
  state?: string
) {
  return useQuery({
    queryKey: ['trendStats', metrics, startYear, endYear, state],
    queryFn: () => fetchTrendStats(metrics, startYear, endYear, state),
    enabled: metrics.length > 0,
  });
}

export function useComparisonStats(
  libraryIds: string[],
  year?: number,
  metrics?: string[]
) {
  return useQuery({
    queryKey: ['comparisonStats', libraryIds, year, metrics],
    queryFn: () => fetchComparisonStats(libraryIds, year, metrics),
    enabled: libraryIds.length > 0,
  });
} 