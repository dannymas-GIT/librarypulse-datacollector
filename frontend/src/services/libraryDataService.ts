import axios from 'axios';
import { apiConfig } from '@/config/api';

export interface UserLibraryPreferences {
  primaryLibraryId: string;
  comparisonLibraryIds: string[];
  setupComplete: boolean;
}

export const libraryDataService = {
  // Save user's library preferences
  saveUserPreferences: async (preferences: UserLibraryPreferences): Promise<boolean> => {
    try {
      // Use the backend API endpoint
      const endpoint = `${apiConfig.backend.endpoints.setup}/preferences`;
      const response = await axios.post(endpoint, {
        primary_library_id: preferences.primaryLibraryId,
        comparison_library_ids: preferences.comparisonLibraryIds,
        setup_complete: false // The backend will determine this
      });
      
      return !!response.data;
    } catch (error) {
      console.error('Error saving preferences:', error);
      
      // Fallback to localStorage in development if API fails
      if (process.env.NODE_ENV === 'development') {
        localStorage.setItem('libraryPreferences', JSON.stringify(preferences));
        return true;
      }
      
      return false;
    }
  },
  
  // Import data for a library
  importLibraryData: async (libraryId: string): Promise<boolean> => {
    try {
      // Use the backend API endpoint
      const endpoint = `${apiConfig.backend.endpoints.setup}/import/library?library_id=${libraryId}`;
      const response = await axios.post(endpoint);
      
      // The actual import happens in the background on the server
      // We just return true here to indicate the import was started
      return true;
    } catch (error) {
      console.error('Error importing library data:', error);
      
      // Fallback to localStorage in development if API fails
      if (process.env.NODE_ENV === 'development') {
        const importedLibraries = JSON.parse(localStorage.getItem('importedLibraries') || '[]');
        if (!importedLibraries.includes(libraryId)) {
          importedLibraries.push(libraryId);
          localStorage.setItem('importedLibraries', JSON.stringify(importedLibraries));
        }
        return true;
      }
      
      return false;
    }
  },
  
  // Import demographic data for multiple ZCTAs
  importDemographicData: async (zctas: string[]): Promise<boolean> => {
    try {
      // Use the backend API endpoint
      const queryParams = zctas.map(zcta => `zctas=${zcta}`).join('&');
      const endpoint = `${apiConfig.backend.endpoints.setup}/import/demographics?${queryParams}`;
      const response = await axios.post(endpoint);
      
      // The actual import happens in the background on the server
      return true;
    } catch (error) {
      console.error('Error importing demographic data:', error);
      
      // Fallback to localStorage in development if API fails
      if (process.env.NODE_ENV === 'development') {
        // Just mark as imported in localStorage
        localStorage.setItem('demographicDataImported', 'true');
        return true;
      }
      
      return false;
    }
  },
  
  // Get user's library preferences
  getUserPreferences: async (): Promise<UserLibraryPreferences | null> => {
    // Define valid library IDs
    const VALID_LIBRARY_IDS = ['NY0001', 'NY0002', 'NY0773'];
    
    try {
      // Try to fetch from the API
      const endpoint = `${apiConfig.backend.endpoints.setup}/preferences`;
      const response = await axios.get(endpoint);
      
      // Filter to only include valid library IDs that we have data for
      const primaryId = response.data.primary_library_id;
      const validPrimaryId = VALID_LIBRARY_IDS.includes(primaryId) ? primaryId : 'NY0773';
      
      const comparisonIds = response.data.comparison_library_ids || [];
      const validComparisonIds = comparisonIds.filter(id => VALID_LIBRARY_IDS.includes(id));
      
      return {
        primaryLibraryId: validPrimaryId,
        comparisonLibraryIds: validComparisonIds.length ? validComparisonIds : ['NY0001', 'NY0002'],
        setupComplete: response.data.setup_complete || true
      };
    } catch (error) {
      console.error('Error fetching user preferences:', error);
      
      // Return mock data as fallback
      const mockPreferences: UserLibraryPreferences = {
        primaryLibraryId: 'NY0773',
        comparisonLibraryIds: ['NY0001', 'NY0002'],
        setupComplete: true
      };
      
      console.log('Using mock user preferences:', mockPreferences);
      return mockPreferences;
    }
  },
  
  // Get list of imported libraries
  getImportedLibraries: async (): Promise<string[]> => {
    try {
      // Use the backend API endpoint
      const endpoint = `${apiConfig.backend.endpoints.setup}/status`;
      const response = await axios.get(endpoint);
      return response.data.imported_libraries || [];
    } catch (error) {
      console.error('Error fetching imported libraries:', error);
      
      // Fallback to localStorage in development if API fails
      if (process.env.NODE_ENV === 'development') {
        const importedLibraries = localStorage.getItem('importedLibraries');
        return importedLibraries ? JSON.parse(importedLibraries) : [];
      }
      
      return [];
    }
  },
  
  // Check if setup is complete
  isSetupComplete: async (): Promise<boolean> => {
    try {
      // Use the backend API endpoint
      const endpoint = `${apiConfig.backend.endpoints.setup}/status`;
      const response = await axios.get(endpoint);
      return response.data.is_complete;
    } catch (error) {
      console.error('Error checking setup status:', error);
      
      // Fallback to localStorage in development if API fails
      if (process.env.NODE_ENV === 'development') {
        // Check if setupComplete flag is set directly
        const setupComplete = localStorage.getItem('setupComplete');
        console.log('Checking setupComplete flag:', setupComplete);
        if (setupComplete === 'true') {
          console.log('Setup is complete based on setupComplete flag');
          return true;
        }
        
        // Check all requirements for setup to be complete:
        // 1. Library preferences should be set
        const preferences = localStorage.getItem('libraryPreferences');
        console.log('Checking library preferences:', preferences);
        if (!preferences) {
          console.log('Setup is incomplete: No library preferences found');
          return false;
        }
        
        const parsedPreferences: UserLibraryPreferences = JSON.parse(preferences);
        console.log('Parsed preferences:', parsedPreferences);
        
        // 2. Primary library should be set
        if (!parsedPreferences.primaryLibraryId) {
          console.log('Setup is incomplete: No primary library set');
          return false;
        }
        
        // 3. At least the primary library should be imported
        const importedLibraries = localStorage.getItem('importedLibraries');
        const parsedImportedLibraries = importedLibraries ? JSON.parse(importedLibraries) : [];
        console.log('Checking imported libraries:', parsedImportedLibraries);
        if (!parsedImportedLibraries.includes(parsedPreferences.primaryLibraryId)) {
          console.log('Setup is incomplete: Primary library not imported');
          return false;
        }
        
        // 4. Demographic data should be present
        const demographicDataImported = localStorage.getItem('demographicDataImported');
        console.log('Checking demographic data imported:', demographicDataImported);
        if (!demographicDataImported) {
          console.log('Setup is incomplete: No demographic data imported');
          return false;
        }
        
        // If all checks pass, setup is complete
        console.log('All setup checks passed, setup is complete');
        return true;
      }
      
      return false;
    }
  },
  
  // Get import status
  getImportStatus: async (): Promise<any> => {
    try {
      // Use the backend API endpoint
      const endpoint = `${apiConfig.backend.endpoints.setup}/status`;
      const response = await axios.get(endpoint);
      return response.data;
    } catch (error) {
      console.error('Error getting import status:', error);
      return null;
    }
  },
  
  // Reset all application data (for testing)
  resetAppData: async (): Promise<boolean> => {
    try {
      // Use the backend API endpoint
      const endpoint = `${apiConfig.backend.endpoints.setup}/reset`;
      const response = await axios.post(endpoint);
      return response.data.success;
    } catch (error) {
      console.error('Error resetting app data:', error);
      
      // Fallback to localStorage in development if API fails
      if (process.env.NODE_ENV === 'development') {
        localStorage.removeItem('libraryPreferences');
        localStorage.removeItem('importedLibraries');
        localStorage.removeItem('demographicDataImported');
        return true;
      }
      
      return false;
    }
  }
};

export default libraryDataService; 