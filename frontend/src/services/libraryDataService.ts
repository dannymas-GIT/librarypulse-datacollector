import axios from 'axios';

export interface UserLibraryPreferences {
  primaryLibraryId: string;
  comparisonLibraryIds: string[];
}

export const libraryDataService = {
  // Save user's library preferences
  saveUserPreferences: async (preferences: UserLibraryPreferences): Promise<boolean> => {
    try {
      // For now, we'll simulate this with localStorage since we don't have the backend endpoint yet
      localStorage.setItem('libraryPreferences', JSON.stringify(preferences));
      return true;
      
      // When backend is ready:
      // const response = await axios.post('/api/user/preferences', preferences);
      // return response.data.success;
    } catch (error) {
      console.error('Error saving preferences:', error);
      return false;
    }
  },
  
  // Import data for a library
  importLibraryData: async (libraryId: string): Promise<boolean> => {
    try {
      // For now, we'll simulate this with a delay
      await new Promise(resolve => setTimeout(resolve, 1500));
      return true;
      
      // When backend is ready:
      // const response = await axios.post('/api/data/import', { libraryId });
      // return response.data.success;
    } catch (error) {
      console.error('Error importing library data:', error);
      return false;
    }
  },
  
  // Get user's library preferences
  getUserPreferences: async (): Promise<UserLibraryPreferences | null> => {
    try {
      // For now, we'll get this from localStorage
      const preferences = localStorage.getItem('libraryPreferences');
      return preferences ? JSON.parse(preferences) : null;
      
      // When backend is ready:
      // const response = await axios.get('/api/user/preferences');
      // return response.data;
    } catch (error) {
      console.error('Error fetching user preferences:', error);
      return null;
    }
  },
  
  // Check if setup is complete
  isSetupComplete: async (): Promise<boolean> => {
    try {
      // For now, we'll check localStorage
      const preferences = localStorage.getItem('libraryPreferences');
      return !!preferences;
      
      // When backend is ready:
      // const response = await axios.get('/api/user/setup-status');
      // return response.data.isComplete;
    } catch (error) {
      console.error('Error checking setup status:', error);
      return false;
    }
  }
};

export default libraryDataService; 