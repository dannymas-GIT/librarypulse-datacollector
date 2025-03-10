/**
 * Global configuration for the application
 */

// API configuration
export const API_BASE_URL = 'http://localhost:8000/api/v1';
export const HISTORICAL_API_URL = 'http://localhost:8000/api/historical';

// Application settings
export const APP_NAME = 'IMLS Library Pulse';
export const APP_VERSION = '1.0.0';

// Feature flags
export const FEATURES = {
  ENABLE_COMPARE: false, // Compare feature is disabled for now
  USE_MOCK_DATA: false, // Set to false to use real data from API
}; 