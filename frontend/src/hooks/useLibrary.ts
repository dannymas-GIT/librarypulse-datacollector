import { useState, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  getLibrary, 
  getLibraryOutlets, 
  getLibraryStatistics, 
  getLibraryTrends,
  Library,
  LibraryOutlet,
  LibraryFilters,
  PaginatedResponse
} from '@/services/libraryService';
import { getLibraries } from '@/services/libraryService';

export function useLibraryDetails(libraryId: number | null) {
  return useQuery({
    queryKey: ['library', libraryId],
    queryFn: () => getLibrary(libraryId!),
    enabled: !!libraryId,
  });
}

export function useLibraryOutlets(libraryId: number | null) {
  return useQuery({
    queryKey: ['libraryOutlets', libraryId],
    queryFn: () => getLibraryOutlets(libraryId!),
    enabled: !!libraryId,
  });
}

export function useLibraryStatistics(
  libraryId: number | null, 
  year?: number
) {
  return useQuery({
    queryKey: ['libraryStatistics', libraryId, year],
    queryFn: () => getLibraryStatistics(libraryId!, year),
    enabled: !!libraryId,
  });
}

export function useLibraryTrends(
  libraryId: number | null, 
  metric: string, 
  startYear?: number, 
  endYear?: number
) {
  return useQuery({
    queryKey: ['libraryTrends', libraryId, metric, startYear, endYear],
    queryFn: () => getLibraryTrends(libraryId!, metric, startYear, endYear),
    enabled: !!libraryId && !!metric,
  });
}

export function useLibrarySearch() {
  const [searchParams, setSearchParams] = useState<LibraryFilters>({
    state: '',
    city: '',
    type: '',
    population_min: undefined,
    population_max: undefined,
    search: '',
    page: 1,
    limit: 10,
  });

  const updateSearchParams = useCallback((params: Partial<LibraryFilters>) => {
    setSearchParams(prev => ({
      ...prev,
      ...params,
      // Reset to page 1 when search criteria change
      ...(Object.keys(params).some(key => key !== 'page') ? { page: 1 } : {}),
    }));
  }, []);

  const { data, isLoading, error } = useQuery({
    queryKey: ['libraries', searchParams],
    queryFn: () => {
      // Filter out undefined values
      const filteredParams = Object.entries(searchParams).reduce(
        (acc, [key, value]) => {
          if (value !== undefined && value !== '') {
            acc[key] = value;
          }
          return acc;
        },
        {} as Record<string, any>
      );
      
      return getLibraries(filteredParams);
    },
  });

  return {
    libraries: data?.items || [],
    total: data?.total || 0,
    page: data?.page || 1,
    limit: data?.limit || 10,
    pages: data?.pages || 1,
    isLoading,
    error,
    searchParams,
    updateSearchParams,
  };
} 