import axios, { AxiosError, AxiosRequestConfig } from 'axios';

// Create an axios instance with default config
export const api = axios.create({
  baseURL: '/',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Error handling
export interface ApiError {
  status: number;
  message: string;
  details?: any;
}

export const handleApiError = (error: unknown): ApiError => {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError;
    return {
      status: axiosError.response?.status || 500,
      message: axiosError.response?.data?.detail || axiosError.message || 'Unknown error',
      details: axiosError.response?.data,
    };
  }
  
  return {
    status: 500,
    message: error instanceof Error ? error.message : 'Unknown error',
  };
};

// Generic API request function with error handling
export const apiRequest = async <T>(
  config: AxiosRequestConfig
): Promise<T> => {
  try {
    const response = await api(config);
    return response.data as T;
  } catch (error) {
    throw handleApiError(error);
  }
};

// Helper functions for common HTTP methods
export const get = <T>(url: string, params?: any): Promise<T> => {
  return apiRequest<T>({ method: 'GET', url, params });
};

export const post = <T>(url: string, data?: any): Promise<T> => {
  return apiRequest<T>({ method: 'POST', url, data });
};

export const put = <T>(url: string, data?: any): Promise<T> => {
  return apiRequest<T>({ method: 'PUT', url, data });
};

export const del = <T>(url: string): Promise<T> => {
  return apiRequest<T>({ method: 'DELETE', url });
}; 