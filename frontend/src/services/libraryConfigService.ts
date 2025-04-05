import axios from 'axios';
import { API_BASE_URL } from '../config';

const API_URL = `${API_BASE_URL}/library-config`;

export interface LibrarySearchResult {
  id: string;
  name: string;
  city?: string;
  state?: string;
}

export interface MetricCategory {
  [key: string]: string;
}

export interface MetricsConfig {
  categories: {
    collection: MetricCategory;
    usage: MetricCategory;
    program: MetricCategory;
    staff: MetricCategory;
    financial: MetricCategory;
  };
}

export interface LibraryConfig {
  id: number;
  library_id: string;
  library_name: string;
  collection_stats_enabled: boolean;
  usage_stats_enabled: boolean;
  program_stats_enabled: boolean;
  staff_stats_enabled: boolean;
  financial_stats_enabled: boolean;
  collection_metrics?: Record<string, boolean>;
  usage_metrics?: Record<string, boolean>;
  program_metrics?: Record<string, boolean>;
  staff_metrics?: Record<string, boolean>;
  financial_metrics?: Record<string, boolean>;
  comparison_libraries?: LibrarySearchResult[];
  setup_complete: boolean;
  auto_update_enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface LibraryConfigCreate {
  library_id: string;
  library_name: string;
  collection_stats_enabled: boolean;
  usage_stats_enabled: boolean;
  program_stats_enabled: boolean;
  staff_stats_enabled: boolean;
  financial_stats_enabled: boolean;
  collection_metrics?: Record<string, boolean>;
  usage_metrics?: Record<string, boolean>;
  program_metrics?: Record<string, boolean>;
  staff_metrics?: Record<string, boolean>;
  financial_metrics?: Record<string, boolean>;
  comparison_libraries?: LibrarySearchResult[];
  setup_complete: boolean;
  auto_update_enabled: boolean;
}

export interface LibraryConfigUpdate {
  collection_stats_enabled?: boolean;
  usage_stats_enabled?: boolean;
  program_stats_enabled?: boolean;
  staff_stats_enabled?: boolean;
  financial_stats_enabled?: boolean;
  collection_metrics?: Record<string, boolean>;
  usage_metrics?: Record<string, boolean>;
  program_metrics?: Record<string, boolean>;
  staff_metrics?: Record<string, boolean>;
  financial_metrics?: Record<string, boolean>;
  setup_complete?: boolean;
  auto_update_enabled?: boolean;
}

export interface SetupStatus {
  setup_complete: boolean;
}

export const libraryConfigService = {
  getSetupStatus: async (): Promise<SetupStatus> => {
    const response = await axios.get<SetupStatus>(`${API_URL}/setup-status`);
    return response.data;
  },

  getConfig: async (): Promise<LibraryConfig> => {
    const response = await axios.get<LibraryConfig>(`${API_URL}/config`);
    return response.data;
  },

  createConfig: async (config: LibraryConfigCreate): Promise<LibraryConfig> => {
    const response = await axios.post<LibraryConfig>(`${API_URL}/config`, config);
    return response.data;
  },

  updateConfig: async (config: LibraryConfigUpdate): Promise<LibraryConfig> => {
    const response = await axios.patch<LibraryConfig>(`${API_URL}/config`, config);
    return response.data;
  },

  searchLibraries: async (query: string, limit: number = 10): Promise<LibrarySearchResult[]> => {
    const response = await axios.get<LibrarySearchResult[]>(`${API_URL}/libraries/search`, {
      params: { query, limit }
    });
    return response.data;
  },

  getAvailableMetrics: async (): Promise<MetricsConfig> => {
    const response = await axios.get<MetricsConfig>(`${API_URL}/metrics`);
    return response.data;
  }
}; 