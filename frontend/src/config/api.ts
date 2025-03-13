/**
 * API Configuration
 * 
 * This file contains configuration settings for external APIs used in the application.
 * In a production environment, sensitive values like API keys should be stored in
 * environment variables and not committed to the repository.
 */

export const apiConfig = {
  census: {
    // Census API key - in a real app, this would be stored in environment variables
    // You can get a free API key from https://api.census.gov/data/key_signup.html
    apiKey: 'YOUR_CENSUS_API_KEY',
    
    // Base URL for Census API
    baseUrl: 'https://api.census.gov/data',
    
    // Latest ACS 5-year estimates dataset
    acsDataset: '2021/acs/acs5',
    
    // Whether to use live Census API data or fall back to mock data
    useLiveData: false, // Set to false to use mock data since we don't have live setup endpoints
  },
  
  // Backend API configuration
  backend: {
    baseUrl: 'http://localhost:8000', // Make sure this points to your FastAPI backend
    
    // Endpoints - updated to match actual backend API structure
    endpoints: {
      demographics: '/demographics',
      libraries: '/api/libraries',
      statistics: '/api/historical',
      dashboard: '/api/dashboard',
      // Note: The setup endpoint doesn't exist in the backend API
      // Using mock data for setup-related functionality
      setup: '/api/setup', // This will fall back to mock data
      libraryConfig: '/api/library-config', // This will fall back to mock data
    },
    
    // Flag to control whether to use live data or mock data
    useLiveData: false, // Set to false to use mock data for missing endpoints
  },
};

export default apiConfig; 