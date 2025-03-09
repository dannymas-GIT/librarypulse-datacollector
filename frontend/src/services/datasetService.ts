import { get, post, put, del } from '@/utils/api';

export interface Dataset {
  id: number;
  year: number;
  name: string;
  description: string;
  source_url: string;
  file_path: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  record_count: number | null;
  processed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface DatasetFilters {
  year?: number;
  status?: 'pending' | 'processing' | 'completed' | 'failed';
  page?: number;
  limit?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface DatasetUpload {
  year: number;
  name: string;
  description: string;
  file: File;
}

export interface DatasetProcessingStatus {
  id: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  message: string | null;
}

// Get a paginated list of datasets with optional filters
export const getDatasets = (filters: DatasetFilters = {}): Promise<PaginatedResponse<Dataset>> => {
  return get<PaginatedResponse<Dataset>>('/datasets', filters);
};

// Get a single dataset by ID
export const getDataset = (id: number): Promise<Dataset> => {
  return get<Dataset>(`/datasets/${id}`);
};

// Upload a new dataset
export const uploadDataset = (data: DatasetUpload): Promise<Dataset> => {
  const formData = new FormData();
  formData.append('year', data.year.toString());
  formData.append('name', data.name);
  formData.append('description', data.description);
  formData.append('file', data.file);

  return post<Dataset>('/datasets/upload', formData);
};

// Process a dataset
export const processDataset = (id: number): Promise<Dataset> => {
  return post<Dataset>(`/datasets/${id}/process`, {});
};

// Get the processing status of a dataset
export const getDatasetProcessingStatus = (id: number): Promise<DatasetProcessingStatus> => {
  return get<DatasetProcessingStatus>(`/datasets/${id}/status`);
};

// Delete a dataset
export const deleteDataset = (id: number): Promise<void> => {
  return del<void>(`/datasets/${id}`);
};

// Get summary statistics for all datasets
export const getDatasetsSummary = (): Promise<{
  total: number;
  by_year: { year: number; count: number }[];
  by_status: { status: string; count: number }[];
}> => {
  return get<{
    total: number;
    by_year: { year: number; count: number }[];
    by_status: { status: string; count: number }[];
  }>('/datasets/summary');
};

// Get available years for data
export const getAvailableYears = (): Promise<number[]> => {
  return get<number[]>('/datasets/years');
}; 