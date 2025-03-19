import { useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';

interface SetupStatus {
  isSetupComplete: boolean;
}

export const useSetup = () => {
  const { data, isLoading } = useQuery<SetupStatus>({
    queryKey: ['setup-status'],
    queryFn: async () => {
      const response = await api.get('/api/v1/setup/status');
      return response.data;
    },
  });

  return {
    isSetupComplete: data?.isSetupComplete ?? false,
    isLoading,
  };
}; 