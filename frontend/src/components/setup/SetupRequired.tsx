import React from 'react';
import { Navigate } from 'react-router-dom';
import { useSetup } from '@/hooks/useSetup';

interface SetupRequiredProps {
  children: React.ReactNode;
}

export const SetupRequired: React.FC<SetupRequiredProps> = ({ children }) => {
  const { isSetupComplete, isLoading } = useSetup();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!isSetupComplete) {
    return <Navigate to="/setup" replace />;
  }

  return <>{children}</>;
}; 