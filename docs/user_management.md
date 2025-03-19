# User Management System

This document provides context and technical details for the user management system in the Library Pulse application.

## Overview

The user management system provides authentication, authorization, and user preference management for the Library Pulse application. It enables different types of users (administrators, librarians, analysts, and regular users) to access appropriate features and manage their preferences.

## Database Schema

### User Model

The `User` model represents a user in the system with the following attributes:

- **id**: Unique identifier
- **email**: User's email address (unique)
- **username**: User's username (unique)
- **hashed_password**: Securely hashed password
- **is_active**: Whether the user account is active
- **is_verified**: Whether the user's email has been verified
- **verification_token**: Token for email verification
- **verification_token_expires**: Expiration time for verification token
- **password_reset_token**: Token for password reset
- **password_reset_token_expires**: Expiration time for password reset token
- **last_login**: Timestamp of last login
- **first_name**: User's first name
- **last_name**: User's last name
- **role**: User's role (admin, librarian, analyst, user)
- **library_id**: Associated library ID (for librarians)
- **created_at**: Timestamp of account creation
- **updated_at**: Timestamp of last update

### User Session Model

The `UserSession` model tracks user sessions:

- **id**: Unique identifier
- **user_id**: Associated user ID
- **session_token**: Unique session token
- **expires_at**: Session expiration time
- **ip_address**: IP address used for session
- **user_agent**: Browser/client information
- **is_active**: Whether the session is active
- **created_at**: Session creation timestamp
- **updated_at**: Session update timestamp

### User Preference Model

The `UserPreference` model stores user preferences:

- **id**: Unique identifier
- **user_id**: Associated user ID
- **theme**: UI theme preference
- **dashboard_layout**: Custom dashboard layout
- **default_library_id**: Default library for views
- **default_comparison_library_ids**: Default libraries for comparison
- **default_metrics**: Default metrics to display
- **email_notifications**: Whether to send email notifications
- **created_at**: Preference creation timestamp
- **updated_at**: Preference update timestamp

## Authentication Flow

1. **Registration**:
   - User submits registration form with email, username, password
   - System validates input and checks for existing users
   - System creates new user with hashed password
   - System sends verification email
   - User verifies email to activate account

2. **Login**:
   - User submits login form with email/username and password
   - System validates credentials
   - System creates new session and returns JWT token
   - Frontend stores token for subsequent requests

3. **Password Reset**:
   - User requests password reset with email
   - System generates reset token and sends email
   - User clicks link and enters new password
   - System validates token and updates password

## Authorization System

The system implements role-based access control with the following roles:

1. **Admin**:
   - Full access to all features
   - User management capabilities
   - System configuration
   - Data management

2. **Librarian**:
   - Access to their library's data
   - Limited comparison capabilities
   - Report generation for their library

3. **Analyst**:
   - Access to all library data
   - Advanced analytics features
   - Report generation

4. **User**:
   - Basic access to public library data
   - Limited comparison capabilities
   - No administrative functions

## API Endpoints

The following API endpoints have been implemented:

### Authentication

- `POST /api/v1/auth/register`: Register a new user
- `POST /api/v1/auth/login`: Authenticate and get token
- `POST /api/v1/auth/logout`: Invalidate current session
- `GET /api/v1/auth/verify-email/{token}`: Verify email address
- `POST /api/v1/auth/forgot-password`: Request password reset
- `POST /api/v1/auth/reset-password/{token}`: Reset password with token

### User Management

- `GET /api/v1/users/me`: Get current user profile
- `PUT /api/v1/users/me`: Update current user profile
- `GET /api/v1/users/preferences`: Get user preferences
- `PUT /api/v1/users/preferences`: Update user preferences
- `GET /api/v1/users`: List users (admin only)
- `POST /api/v1/users`: Create new user (admin only)
- `GET /api/v1/users/{user_id}`: Get user by ID (admin only)
- `PUT /api/v1/users/{user_id}`: Update user (admin only)
- `DELETE /api/v1/users/{user_id}`: Delete user (admin only)

## Frontend Components (To Be Implemented)

The following frontend components will be implemented:

1. **Authentication Pages**:
   - Login page
   - Registration page
   - Password reset request page
   - Password reset page
   - Email verification page

2. **User Profile Components**:
   - Profile view/edit
   - Password change
   - Preferences management

3. **Admin Components**:
   - User management dashboard
   - User creation/editing forms
   - Role management

## Security Considerations

- Passwords are hashed using bcrypt with appropriate work factor
- JWT tokens are signed with a secure key
- CSRF protection is implemented for all forms
- Rate limiting is applied to authentication endpoints
- Input validation is performed on all user inputs
- Sessions expire after a configurable period of inactivity
- Failed login attempts are tracked and limited

## Implementation Status

- ✅ Database models created
- ✅ Authentication API endpoints
- ✅ User management API endpoints
- ⬜ Frontend authentication components
- ⬜ Frontend user management components
- ⬜ Role-based access control implementation
- ⬜ User preferences implementation

## Next Steps

1. **Frontend Authentication Implementation**
   - Create React components for login, registration, and password reset
   - Implement JWT token storage and management
   - Add form validation and error handling
   - Design responsive UI for authentication pages

2. **User Profile and Preferences UI**
   - Build user profile page with edit functionality
   - Create preferences management interface
   - Implement theme switching
   - Add default library and metrics selection

3. **Admin Dashboard**
   - Develop user management interface
   - Create user listing with filtering and pagination
   - Build user creation and editing forms
   - Implement role assignment functionality

4. **Role-Based Access Control**
   - Add route protection based on user roles
   - Create role-specific navigation components
   - Implement permission checks in UI components
   - Add conditional rendering based on user roles

5. **Testing and Integration**
   - Write unit tests for authentication components
   - Perform integration testing of the complete authentication flow
   - Test role-based access restrictions
   - Validate user preference functionality

## Technical Implementation Details

### Frontend Authentication

The frontend authentication will use React Query for managing authentication state and API calls. JWT tokens will be stored in localStorage with appropriate security measures. The authentication flow will include:

```typescript
// Example authentication hook
const useAuth = () => {
  const queryClient = useQueryClient();
  
  const login = useMutation({
    mutationFn: (credentials: LoginCredentials) => 
      authService.login(credentials),
    onSuccess: (data) => {
      localStorage.setItem('token', data.access_token);
      queryClient.setQueryData(['user'], data.user);
    }
  });
  
  const logout = () => {
    localStorage.removeItem('token');
    queryClient.clear();
  };
  
  return { login, logout };
};
```

### Protected Routes

Protected routes will be implemented using a higher-order component or custom hook:

```typescript
// Example protected route component
const ProtectedRoute = ({ 
  children, 
  requiredRole 
}: ProtectedRouteProps) => {
  const { user, isLoading } = useUser();
  
  if (isLoading) {
    return <LoadingSpinner />;
  }
  
  if (!user) {
    return <Navigate to="/login" />;
  }
  
  if (requiredRole && user.role !== requiredRole) {
    return <Navigate to="/unauthorized" />;
  }
  
  return <>{children}</>;
};
``` 