export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterCredentials extends LoginCredentials {
  username: string;
  firstName: string;
  lastName: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface User {
  id: number;
  email: string;
  username: string;
  firstName: string;
  lastName: string;
  role: 'admin' | 'librarian' | 'analyst' | 'user';
  isActive: boolean;
  isVerified: boolean;
  libraryId?: number;
  createdAt: string;
  updatedAt: string;
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'system';
  dashboardLayout: string;
  defaultLibraryId?: number;
  defaultComparisonLibraryIds?: number[];
  defaultMetrics: string[];
  emailNotifications: boolean;
} 