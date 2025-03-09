import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';

import { libraryConfigService } from '../../services/libraryConfigService';

const SetupRequired: React.FC = () => {
  // Check setup status
  const { data, isLoading } = useQuery({
    queryKey: ['setupStatus'],
    queryFn: () => libraryConfigService.getSetupStatus(),
  });
  
  // Show a loading indicator while checking
  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin w-8 h-8 border-4 border-blue-500 rounded-full border-t-transparent"></div>
      </div>
    );
  }
  
  // If setup is not complete, redirect to setup wizard
  if (!data?.setup_complete) {
    return <Navigate to="/setup" replace />;
  }
  
  // Otherwise, render the child routes
  return <Outlet />;
};

export default SetupRequired; 