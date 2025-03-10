import axios, { AxiosResponse } from 'axios';

/**
 * Service for interacting with the historical data API
 */

// Define the direct URL to avoid config import issues
const HISTORICAL_API_URL = 'http://localhost:8000/api/historical';

console.log('Initializing historical service with API URL:', HISTORICAL_API_URL);

// Configure axios for the historical data API
const axiosInstance = axios.create({
  baseURL: HISTORICAL_API_URL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Cache-Control': 'no-cache',
  },
  timeout: 15000, // 15 seconds timeout
});

// Add response interceptor for logging
axiosInstance.interceptors.response.use(
  (response) => {
    console.log(`SUCCESS: ${response.config.method?.toUpperCase()} ${response.config.url}`, response.status);
    return response;
  },
  (error) => {
    if (error.response) {
      console.error(`ERROR ${error.response.status}: ${error.config.method?.toUpperCase()} ${error.config.url}`, error.response.data);
    } else if (error.request) {
      console.error('ERROR: No response received', error.request);
    } else {
      console.error('ERROR:', error.message);
    }
    return Promise.reject(error);
  }
);

// Add request interceptor for logging
axiosInstance.interceptors.request.use(
  (config) => {
    console.log(`REQUEST: ${config.method?.toUpperCase()} ${config.url}`, config.params || {});
    return config;
  },
  (error) => {
    console.error('Request error:', error);
    return Promise.reject(error);
  }
);

// Export types for historical data
export interface HistoricalSummary {
  library_id: string;
  name: string;
  years_available: number[];
  earliest_year: number;
  latest_year: number;
  total_years: number;
  metrics_available: string[];
}

export interface LibraryHistoricalData {
  id: number;
  library_id: string;
  year: number;
  name: string;
  address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  county?: string;
  phone?: string;
  locale?: string;
  central_library_count?: number;
  branch_library_count?: number;
  bookmobile_count?: number;
  service_area_population?: number;
  print_collection?: number;
  electronic_collection?: number;
  audio_collection?: number;
  video_collection?: number;
  total_circulation?: number;
  electronic_circulation?: number;
  physical_circulation?: number;
  visits?: number;
  reference_transactions?: number;
  registered_users?: number;
  public_internet_computers?: number;
  public_wifi_sessions?: number;
  website_visits?: number;
  total_programs?: number;
  total_program_attendance?: number;
  children_programs?: number;
  children_program_attendance?: number;
  ya_programs?: number;
  ya_program_attendance?: number;
  adult_programs?: number;
  adult_program_attendance?: number;
  total_staff?: number;
  librarian_staff?: number;
  mls_librarian_staff?: number;
  other_staff?: number;
  total_operating_revenue?: number;
  local_operating_revenue?: number;
  state_operating_revenue?: number;
  federal_operating_revenue?: number;
  other_operating_revenue?: number;
  total_operating_expenditures?: number;
  staff_expenditures?: number;
  collection_expenditures?: number;
}

export interface TrendData {
  metric: string;
  years: number[];
  values: (number | null)[];
  growth_rates?: {
    yearly?: Record<string, number>;
    average?: number;
    total?: number;
  };
}

class HistoricalService {
  /**
   * Get a summary of the historical data
   */
  async getSummary(libraryId: string = 'NY0773'): Promise<HistoricalSummary> {
    console.log('Fetching historical data summary');
    try {
      const response: AxiosResponse<HistoricalSummary> = await axiosInstance.get('/summary', {
        params: { library_id: libraryId }
      });
      console.log('Summary data received:', response.data);
      return response.data;
    } catch (error) {
      console.error('Error fetching summary:', error);
      throw error;
    }
  }

  /**
   * Get all available years
   */
  async getYears(libraryId: string = 'NY0773'): Promise<number[]> {
    console.log('Fetching available years');
    try {
      const response: AxiosResponse<number[]> = await axiosInstance.get('/years', {
        params: { library_id: libraryId }
      });
      console.log('Years received:', response.data);
      return response.data;
    } catch (error) {
      console.error('Error fetching years:', error);
      throw error;
    }
  }

  /**
   * Get data for a specific year
   */
  async getDataForYear(year: number, libraryId: string = 'NY0773'): Promise<LibraryHistoricalData> {
    console.log(`Fetching data for year ${year}`);
    try {
      const response: AxiosResponse<LibraryHistoricalData> = await axiosInstance.get(`/data/${year}`, {
        params: { library_id: libraryId }
      });
      console.log(`Data for year ${year} received:`, response.data);
      return response.data;
    } catch (error) {
      console.error(`Error fetching data for year ${year}:`, error);
      throw error;
    }
  }

  /**
   * Get all historical data
   */
  async getAllData(libraryId: string = 'NY0773'): Promise<LibraryHistoricalData[]> {
    console.log('Fetching all historical data');
    try {
      const response: AxiosResponse<LibraryHistoricalData[]> = await axiosInstance.get('/data', {
        params: { library_id: libraryId }
      });
      console.log('All historical data received:', response.data.length, 'records');
      return response.data;
    } catch (error) {
      console.error('Error fetching all data:', error);
      throw error;
    }
  }

  /**
   * Get trend data for a specific metric
   */
  async getTrendData(metric: string, libraryId: string = 'NY0773'): Promise<TrendData> {
    console.log(`Fetching trend data for metric: ${metric}`);
    try {
      const response: AxiosResponse<TrendData> = await axiosInstance.get(`/trends/${metric}`, {
        params: { library_id: libraryId }
      });
      console.log(`Trend data for ${metric} received:`, response.data);
      return response.data;
    } catch (error) {
      console.error(`Error fetching trend data for ${metric}:`, error);
      throw error;
    }
  }

  /**
   * Get trend data for multiple metrics
   */
  async getMultipleTrendData(metrics: string[], libraryId: string = 'NY0773'): Promise<TrendData[]> {
    console.log(`Fetching trend data for metrics: ${metrics.join(', ')}`);
    
    try {
      // Method 1: Use manual URL construction
      let url = '/trends?';
      metrics.forEach((metric, index) => {
        url += `metrics=${encodeURIComponent(metric)}`;
        if (index < metrics.length - 1) {
          url += '&';
        }
      });
      
      if (libraryId) {
        url += `&library_id=${encodeURIComponent(libraryId)}`;
      }
      
      console.log('Making request to URL:', HISTORICAL_API_URL + url);
      
      const response: AxiosResponse<TrendData[]> = await axiosInstance.get(url);
      console.log(`Trend data for multiple metrics received:`, response.data);
      return response.data;
      
      /* 
      // Method 2: Alternative approach with params object 
      const response = await axiosInstance.get('/trends', {
        params: {
          metrics: metrics,
          library_id: libraryId
        },
        paramsSerializer: (params) => {
          const searchParams = new URLSearchParams();
          
          // Handle array parameters
          Object.entries(params).forEach(([key, value]) => {
            if (Array.isArray(value)) {
              value.forEach(v => searchParams.append(key, v));
            } else {
              searchParams.append(key, value);
            }
          });
          
          return searchParams.toString();
        }
      });
      */
    } catch (error) {
      console.error(`Error fetching multiple trend data:`, error);
      throw error;
    }
  }
}

export const historicalService = new HistoricalService(); 