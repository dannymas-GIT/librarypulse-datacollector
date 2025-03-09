import { useState, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  getDatasets, 
  getDataset, 
  uploadDataset, 
  processDataset, 
  getDatasetProcessingStatus, 
  deleteDataset, 
  getDatasetsSummary,
  Dataset,
  DatasetFilters,
  DatasetUpload,
  DatasetProcessingStatus,
  PaginatedResponse
} from '@/services/datasetService';
import { useToast } from '@/contexts/ToastContext';

export function useDatasetList() {
  const [filters, setFilters] = useState<DatasetFilters>({
    page: 1,
    limit: 10,
  });

  const updateFilters = useCallback((newFilters: Partial<DatasetFilters>) => {
    setFilters(prev => ({
      ...prev,
      ...newFilters,
      // Reset to page 1 when filters change (except when changing page)
      ...(Object.keys(newFilters).some(key => key !== 'page') ? { page: 1 } : {}),
    }));
  }, []);

  const { data, isLoading, error } = useQuery({
    queryKey: ['datasets', filters],
    queryFn: () => getDatasets(filters),
  });

  return {
    datasets: data?.items || [],
    total: data?.total || 0,
    page: data?.page || 1,
    limit: data?.limit || 10,
    pages: data?.pages || 1,
    isLoading,
    error,
    filters,
    updateFilters,
  };
}

export function useDatasetDetails(datasetId: number | null) {
  return useQuery({
    queryKey: ['dataset', datasetId],
    queryFn: () => getDataset(datasetId!),
    enabled: !!datasetId,
  });
}

export function useDatasetProcessingStatus(datasetId: number | null) {
  return useQuery({
    queryKey: ['datasetStatus', datasetId],
    queryFn: () => getDatasetProcessingStatus(datasetId!),
    enabled: !!datasetId,
    // Poll every 2 seconds for status updates
    refetchInterval: 2000,
  });
}

export function useDatasetsSummary() {
  return useQuery({
    queryKey: ['datasetsSummary'],
    queryFn: () => getDatasetsSummary(),
  });
}

export function useDatasetUpload() {
  const queryClient = useQueryClient();
  const { showToast } = useToast();

  return useMutation({
    mutationFn: (data: DatasetUpload) => uploadDataset(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['datasets'] });
      queryClient.invalidateQueries({ queryKey: ['datasetsSummary'] });
      showToast('success', 'Dataset uploaded successfully');
    },
    onError: (error: any) => {
      showToast('error', `Failed to upload dataset: ${error.message}`);
    },
  });
}

export function useDatasetProcess() {
  const queryClient = useQueryClient();
  const { showToast } = useToast();

  return useMutation({
    mutationFn: (datasetId: number) => processDataset(datasetId),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['datasets'] });
      queryClient.invalidateQueries({ queryKey: ['dataset', data.id] });
      queryClient.invalidateQueries({ queryKey: ['datasetStatus', data.id] });
      showToast('success', 'Dataset processing started');
    },
    onError: (error: any) => {
      showToast('error', `Failed to process dataset: ${error.message}`);
    },
  });
}

export function useDatasetDelete() {
  const queryClient = useQueryClient();
  const { showToast } = useToast();

  return useMutation({
    mutationFn: (datasetId: number) => deleteDataset(datasetId),
    onSuccess: (_, datasetId) => {
      queryClient.invalidateQueries({ queryKey: ['datasets'] });
      queryClient.invalidateQueries({ queryKey: ['datasetsSummary'] });
      showToast('success', 'Dataset deleted successfully');
    },
    onError: (error: any) => {
      showToast('error', `Failed to delete dataset: ${error.message}`);
    },
  });
} 