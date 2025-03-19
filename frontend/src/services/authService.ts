import axios from 'axios';
import { RegisterCredentials, AuthResponse, User, UserPreferences } from '../types/auth';

// API base URL - Use relative URL for proxy to work correctly
const API_URL = '/api/v1';

// Types
export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  firstName: string;
  lastName: string;
  username: string;
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_at: string;
  user: User;
}

// Create axios instance with base URL
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config: any) => {
    const token = localStorage.getItem('token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: any) => Promise.reject(error)
);

// Auth service methods
const authService = {
  // Login user
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    // Use URLSearchParams for x-www-form-urlencoded format expected by OAuth2
    const formData = new URLSearchParams();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    
    try {
      console.log('Sending login request with credentials:', {
        username: credentials.username,
        password: '******' // Don't log actual password
      });
      
      const response = await api.post('/auth/login', formData.toString(), {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      });
      
      console.log('Login response:', response.data);
      
      if (response.data.access_token) {
        localStorage.setItem('token', response.data.access_token);
      }
      
      return response.data;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  },

  // Register user
  async register(credentials: RegisterCredentials): Promise<AuthResponse> {
    try {
      // Convert frontend camelCase to backend snake_case
      const requestData = {
        email: credentials.email,
        username: credentials.username,
        password: credentials.password,
        password_confirm: credentials.password, // Backend expects password_confirm
        first_name: credentials.firstName,
        last_name: credentials.lastName
      };
      
      console.log('Sending registration request with data:', {
        ...requestData,
        password: '******',
        password_confirm: '******'
      });
      
      const response = await api.post('/auth/register', requestData);
      console.log('Registration response:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('Registration error:', error.response?.data || error);
      throw error;
    }
  },

  // Logout user
  async logout(): Promise<void> {
    await api.post('/auth/logout');
    localStorage.removeItem('token');
  },

  // Get current user
  async getCurrentUser(): Promise<User> {
    const response = await api.get('/users/me');
    return response.data;
  },

  // Request password reset
  async requestPasswordReset(email: string): Promise<void> {
    await api.post('/auth/forgot-password', { email });
  },

  // Reset password with token
  async resetPassword(token: string, password: string): Promise<void> {
    await api.post(`/auth/reset-password/${token}`, { password });
  },

  // Verify email with token
  async verifyEmail(token: string): Promise<void> {
    await api.get(`/auth/verify-email/${token}`);
  },

  // Get user preferences
  async getUserPreferences(): Promise<UserPreferences> {
    const response = await api.get('/users/preferences');
    return response.data;
  },

  // Update user preferences
  async updateUserPreferences(preferences: Partial<UserPreferences>): Promise<UserPreferences> {
    const response = await api.put('/users/preferences', preferences);
    return response.data;
  },

  // Update user profile
  async updateProfile(data: Partial<User>): Promise<User> {
    const response = await api.put('/users/me', data);
    return response.data;
  },
};

export default authService; 