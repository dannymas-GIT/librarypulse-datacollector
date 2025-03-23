declare module '@tanstack/react-query' {
  export class QueryClient {
    constructor(config?: any);
  }
  
  export function QueryClientProvider(props: { 
    client: QueryClient; 
    children: React.ReactNode 
  }): JSX.Element;
  
  export function useQuery<TData = unknown, TError = unknown>(
    options: {
      queryKey: unknown[];
      queryFn?: () => Promise<TData>;
      enabled?: boolean;
      retry?: boolean | number;
      retryDelay?: number;
      staleTime?: number;
      cacheTime?: number;
      refetchInterval?: number;
      refetchIntervalInBackground?: boolean;
      refetchOnWindowFocus?: boolean;
      refetchOnMount?: boolean;
      onSuccess?: (data: TData) => void;
      onError?: (error: TError) => void;
      onSettled?: (data: TData | undefined, error: TError | null) => void;
      select?: (data: TData) => any;
    }
  ): {
    data: TData | undefined;
    error: TError | null;
    isLoading: boolean;
    isSuccess: boolean;
    isError: boolean;
    isIdle: boolean;
    status: 'idle' | 'loading' | 'success' | 'error';
    refetch: () => Promise<any>;
  };

  export function useMutation<TData = unknown, TError = unknown, TVariables = unknown>(
    options: {
      mutationFn: (variables: TVariables) => Promise<TData>;
      onMutate?: (variables: TVariables) => Promise<unknown> | unknown;
      onSuccess?: (data: TData, variables: TVariables, context: unknown) => Promise<unknown> | unknown;
      onError?: (error: TError, variables: TVariables, context: unknown) => Promise<unknown> | unknown;
      onSettled?: (data: TData | undefined, error: TError | null, variables: TVariables, context: unknown) => Promise<unknown> | unknown;
    }
  ): {
    mutate: (variables: TVariables) => void;
    mutateAsync: (variables: TVariables) => Promise<TData>;
    isLoading: boolean;
    isSuccess: boolean;
    isError: boolean;
    isIdle: boolean;
    status: 'idle' | 'loading' | 'success' | 'error';
    data: TData | undefined;
    error: TError | null;
    reset: () => void;
  };

  export function useQueryClient(): {
    invalidateQueries: (queryKey: unknown[]) => Promise<void>;
    setQueryData: (queryKey: unknown[], updater: unknown) => void;
    getQueryData: (queryKey: unknown[]) => unknown;
    refetchQueries: (queryKey: unknown[], options?: { exact?: boolean }) => Promise<void>;
  };
}

declare module '@tanstack/react-query-devtools' {
  export function ReactQueryDevtools(props: { initialIsOpen?: boolean }): JSX.Element;
} 