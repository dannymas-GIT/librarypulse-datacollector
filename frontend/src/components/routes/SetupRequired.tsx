import React from 'react';
import { Outlet } from 'react-router-dom';
// import { useQuery } from '@tanstack/react-query';

// import { libraryConfigService } from '../../services/libraryConfigService';

const SetupRequired: React.FC = () => {
  // Always allow access to the application
  return <Outlet />;
};

export default SetupRequired; 