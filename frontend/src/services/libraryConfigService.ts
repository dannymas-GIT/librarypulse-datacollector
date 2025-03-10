import axios from 'axios';

// Directly use mock data to avoid connection issues
const USE_MOCK_DATA = true;

// WEST BABYLON HARDCODED CONFIG 
// This ensures we always have the West Babylon library data
const WEST_BABYLON_CONFIG: LibraryConfig = {
  id: 1,
  library_id: 'NY0773',
  library_name: 'West Babylon Public Library',
  collection_stats_enabled: true,
  usage_stats_enabled: true,
  program_stats_enabled: true,
  staff_stats_enabled: true,
  financial_stats_enabled: true,
  collection_metrics: {
    print_collection: true,
    electronic_collection: true,
    audio_collection: true,
    video_collection: true
  },
  usage_metrics: {
    total_circulation: true,
    electronic_circulation: true,
    physical_circulation: true, 
    visits: true,
    reference_transactions: true,
    registered_users: true
  },
  program_metrics: {
    total_programs: true,
    total_program_attendance: true
  },
  staff_metrics: {
    total_staff: true,
    librarian_staff: true
  },
  financial_metrics: {
    total_operating_revenue: true,
    total_operating_expenditures: true,
    staff_expenditures: true,
    collection_expenditures: true
  },
  setup_complete: true,
  auto_update_enabled: true,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString()
};

// Sample metrics configuration
const METRICS_CONFIG: MetricsConfig = {
  categories: {
    collection: {
      print_collection: 'Print Collection',
      electronic_collection: 'Electronic Collection',
      audio_collection: 'Audio Collection',
      video_collection: 'Video Collection'
    },
    usage: {
      total_circulation: 'Total Circulation',
      electronic_circulation: 'Electronic Circulation',
      physical_circulation: 'Physical Circulation',
      visits: 'Library Visits',
      reference_transactions: 'Reference Transactions',
      registered_users: 'Registered Users'
    },
    program: {
      total_programs: 'Total Programs',
      total_program_attendance: 'Total Program Attendance'
    },
    staff: {
      total_staff: 'Total Staff',
      librarian_staff: 'Librarian Staff'
    },
    financial: {
      total_operating_revenue: 'Total Revenue',
      total_operating_expenditures: 'Total Expenditures',
      staff_expenditures: 'Staff Expenditures',
      collection_expenditures: 'Collection Expenditures'
    }
  }
};

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

// Create a simplified mock service
export const libraryConfigService = {
  getSetupStatus: async (): Promise<SetupStatus> => {
    console.log('MOCK: Getting setup status');
    return { setup_complete: true };
  },

  getConfig: async (): Promise<LibraryConfig> => {
    console.log('MOCK: Getting library config');
    return WEST_BABYLON_CONFIG;
  },

  createConfig: async (config: LibraryConfigCreate): Promise<LibraryConfig> => {
    console.log('MOCK: Creating library config', config);
    return WEST_BABYLON_CONFIG;
  },

  updateConfig: async (config: LibraryConfigUpdate): Promise<LibraryConfig> => {
    console.log('MOCK: Updating library config', config);
    return WEST_BABYLON_CONFIG;
  },

  searchLibraries: async (query: string, limit: number = 10): Promise<LibrarySearchResult[]> => {
    console.log(`MOCK: Searching libraries with query: ${query}, limit: ${limit}`);
    return [{
      id: 'NY0773',
      name: 'West Babylon Public Library',
      city: 'West Babylon',
      state: 'NY'
    }];
  },

  getAvailableMetrics: async (): Promise<MetricsConfig> => {
    console.log('MOCK: Getting available metrics');
    return METRICS_CONFIG;
  }
}; 