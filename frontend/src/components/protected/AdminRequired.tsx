import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';
import Loading from '../common/Loading';

interface AdminRequiredProps {
  children: React.ReactNode;
}

const AdminRequired: React.FC<AdminRequiredProps> = ({ children }) => {
  const { isAuthenticated, isLoading, user } = useAuth();

  if (isLoading) {
    return <Loading />;
  }

  if (!isAuthenticated || !user?.isAdmin) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

export default AdminRequired; 