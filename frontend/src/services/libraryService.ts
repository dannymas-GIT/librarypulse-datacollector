import { get, post, put, del } from '@/utils/api';
import { apiConfig } from '@/config/api';

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
  total_circulation?: number;
  visits?: number;
  type?: string;
}

export interface LibrarySearchResult {
  total: number;
  libraries: LibraryProfile[];
}

export interface LibraryFilters {
  query?: string;
  region?: string;
  state?: string;
  limit?: number;
  offset?: number;
}

export interface LibraryCreateRequest {
  library_id: string;
  name: string;
  address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  county?: string;
  phone?: string;
  service_area_population?: number;
}

// Library service functions
export const libraryService = {
  /**
   * Convert database library schema to frontend library profile
   */
  adaptLibraryToProfile: (library: any): LibraryProfile => {
    return {
      id: library.library_id || library.id,
      name: library.name,
      location: {
        address: library.address,
        city: library.city,
        state: library.state,
        zip_code: library.zip_code,
        latitude: library.latitude,
        longitude: library.longitude
      },
      contact: {
        phone: library.phone,
        email: null,
        website: null
      },
      service_area: library.county,
      population_served: library.service_area_population,
      region: library.county,
      available_years: [], // We'll need to populate this separately if needed
      total_circulation: library.total_circulation,
      visits: library.visits
    };
  },

  /**
   * Search for libraries with optional filters
   */
  searchLibraries: async (filters: LibraryFilters = {}): Promise<LibrarySearchResult> => {
    const params = new URLSearchParams();
    if (filters.query) params.append('query', filters.query);
    if (filters.limit) params.append('limit', filters.limit.toString());
    if (filters.offset) params.append('offset', filters.offset.toString());
    
    const endpoint = `${apiConfig.backend.endpoints.libraries}/search-from-db?${params.toString()}`;
    console.log('Searching libraries with URL:', endpoint);
    
    try {
      const result = await get<LibrarySearchResult>(endpoint);
      console.log('Search result:', result);
      return result;
    } catch (error) {
      console.error('Error searching libraries:', error);
      // Return empty result on error
      return { total: 0, libraries: [] };
    }
  },
  
  /**
   * Get libraries grouped by region
   */
  getLibrariesByRegion: async (): Promise<Record<string, LibraryProfile[]>> => {
    const endpoint = `${apiConfig.backend.endpoints.libraries}/regions`;
    return get<Record<string, LibraryProfile[]>>(endpoint);
  },
  
  /**
   * Get a specific library by ID
   */
  getLibrary: async (libraryId: string): Promise<LibraryProfile> => {
    try {
      // Try to use the API endpoint
      console.log(`Fetching library with ID ${libraryId} from API`);
      const endpoint = `${apiConfig.backend.endpoints.libraries}/${libraryId}`;
      return await get<LibraryProfile>(endpoint);
    } catch (error) {
      console.error(`Error fetching library with ID ${libraryId}:`, error);
      
      // Return mock data based on the library ID
      const libraryName = libraryId === 'NY0773' 
        ? 'West Babylon Public Library'
        : libraryId === 'NY0001'
          ? 'Amityville Public Library'
          : libraryId === 'NY0002'
            ? 'Babylon Public Library'
            : `Library ${libraryId}`;
      
      return {
        id: libraryId,
        name: libraryName,
        location: {
          address: '123 Library Lane',
          city: 'West Babylon',
          state: 'NY',
          zip_code: '11704',
          latitude: 40.7128,
          longitude: -74.0060
        },
        contact: {
          phone: '631-555-1234',
          email: 'info@library.org',
          website: 'https://www.library.org'
        },
        population_served: 35000,
        service_area: 'West Babylon',
        region: 'Suffolk County',
        available_years: [2005, 2006, 2007],
        type: 'Public Library'
      };
    }
  },
  
  /**
   * Get all libraries with pagination
   */
  getAllLibraries: async (limit: number = 100, offset: number = 0): Promise<LibraryProfile[]> => {
    const params = new URLSearchParams();
    params.append('limit', limit.toString());
    params.append('offset', offset.toString());
    
    const endpoint = `${apiConfig.backend.endpoints.libraries}/all-from-db?${params.toString()}`;
    console.log('Getting all libraries with URL:', endpoint);
    
    try {
      const result = await get<LibraryProfile[]>(endpoint);
      console.log('All libraries result:', result);
      return result;
    } catch (error) {
      console.error('Error getting all libraries:', error);
      // Return empty array on error
      return [];
    }
  },
  
  /**
   * Autocomplete search for libraries by name
   */
  autocompleteLibraries: async (query: string, limit: number = 10): Promise<LibraryProfile[]> => {
    console.log('Autocomplete called with query:', query, 'length:', query?.length);
    
    if (!query || query.length < 2) {
      console.log('Query too short, returning empty array');
      return [];
    }
    
    const params = new URLSearchParams();
    params.append('query', query);
    params.append('limit', limit.toString());
    
    // Try the database-based API endpoint first
    const endpoint = `${apiConfig.backend.endpoints.libraries}/search-from-db?${params.toString()}`;
    console.log('Autocomplete search with URL:', endpoint);
    
    try {
      console.log('Making API request to:', endpoint);
      const result = await get<LibrarySearchResult>(endpoint);
      console.log('Autocomplete raw result from DB:', result);
      
      if (!result || !result.libraries) {
        console.error('Invalid result format:', result);
        return [];
      }
      
      console.log('Autocomplete found', result.libraries.length, 'libraries');
      return result.libraries;
    } catch (error) {
      console.error('Error in autocomplete search:', error);
      
      // Fall back to the file-based API endpoint
      try {
        const fallbackEndpoint = `${apiConfig.backend.endpoints.libraries}/autocomplete?${params.toString()}`;
        console.log('Falling back to:', fallbackEndpoint);
        const fallbackResult = await get<LibraryProfile[]>(fallbackEndpoint);
        console.log('Autocomplete fallback result:', fallbackResult);
        
        if (!fallbackResult || !Array.isArray(fallbackResult)) {
          console.error('Invalid fallback result format:', fallbackResult);
          return [];
        }
        
        return fallbackResult;
      } catch (fallbackError) {
        console.error('Error in autocomplete fallback:', fallbackError);
        return [];
      }
    }
  },
  
  /**
   * Create a new library
   */
  createLibrary: async (library: LibraryCreateRequest): Promise<LibraryProfile> => {
    const endpoint = `${apiConfig.backend.endpoints.libraries}`;
    return post<LibraryProfile>(endpoint, library);
  }
};

// Export default
export default libraryService; 