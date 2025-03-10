import { get, post, put, del } from '@/utils/api';

export interface LibraryLocation {
  address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  latitude?: number;
  longitude?: number;
}

export interface LibraryContact {
  phone?: string;
  email?: string;
  website?: string;
}

export interface LibraryProfile {
  id: string;
  name: string;
  location?: LibraryLocation;
  contact?: LibraryContact;
  service_area?: string;
  population_served?: number;
  region?: string;
  available_years: number[];
}

export interface LibrarySearchResult {
  total: number;
  libraries: LibraryProfile[];
}

export interface LibraryFilters {
  query?: string;
  region?: string;
  limit?: number;
  offset?: number;
}

// Library service functions
export const libraryService = {
  /**
   * Search for libraries with optional filters
   */
  searchLibraries: async (filters: LibraryFilters = {}): Promise<LibrarySearchResult> => {
    const params = new URLSearchParams();
    if (filters.query) params.append('query', filters.query);
    if (filters.region) params.append('region', filters.region);
    if (filters.limit) params.append('limit', filters.limit.toString());
    if (filters.offset) params.append('offset', filters.offset.toString());
    
    return get<LibrarySearchResult>(`/api/libraries/search?${params.toString()}`);
  },
  
  /**
   * Get libraries grouped by region
   */
  getLibrariesByRegion: async (): Promise<Record<string, LibraryProfile[]>> => {
    return get<Record<string, LibraryProfile[]>>('/api/libraries/regions');
  },
  
  /**
   * Get a specific library by ID
   */
  getLibrary: async (libraryId: string): Promise<LibraryProfile> => {
    return get<LibraryProfile>(`/api/libraries/${libraryId}`);
  },
  
  /**
   * Get all libraries with pagination
   */
  getAllLibraries: async (limit: number = 100, offset: number = 0): Promise<LibraryProfile[]> => {
    const params = new URLSearchParams();
    params.append('limit', limit.toString());
    params.append('offset', offset.toString());
    
    return get<LibraryProfile[]>(`/api/libraries?${params.toString()}`);
  }
};

// Export default
export default libraryService; 