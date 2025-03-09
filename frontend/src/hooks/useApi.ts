import { useState, useCallback } from 'react';
import { ApiError, get, post, put, del } from '@/utils/api';

interface ApiState<T> {
  data: T | null;
  loading: boolean;
  error: ApiError | null;
}

interface ApiHook<T> extends ApiState<T> {
  fetchData: (url: string, params?: any) => Promise<void>;
  postData: (url: string, data?: any) => Promise<void>;
  putData: (url: string, data?: any) => Promise<void>;
  deleteData: (url: string) => Promise<void>;
  reset: () => void;
}

export function useApi<T>(): ApiHook<T> {
  const [state, setState] = useState<ApiState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const reset = useCallback(() => {
    setState({
      data: null,
      loading: false,
      error: null,
    });
  }, []);

  const fetchData = useCallback(async (url: string, params?: any) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const data = await get<T>(url, params);
      setState({ data, loading: false, error: null });
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        loading: false, 
        error: error as ApiError 
      }));
    }
  }, []);

  const postData = useCallback(async (url: string, data?: any) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const responseData = await post<T>(url, data);
      setState({ data: responseData, loading: false, error: null });
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        loading: false, 
        error: error as ApiError 
      }));
    }
  }, []);

  const putData = useCallback(async (url: string, data?: any) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const responseData = await put<T>(url, data);
      setState({ data: responseData, loading: false, error: null });
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        loading: false, 
        error: error as ApiError 
      }));
    }
  }, []);

  const deleteData = useCallback(async (url: string) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const responseData = await del<T>(url);
      setState({ data: responseData, loading: false, error: null });
    } catch (error) {
      setState(prev => ({ 
        ...prev, 
        loading: false, 
        error: error as ApiError 
      }));
    }
  }, []);

  return {
    ...state,
    fetchData,
    postData,
    putData,
    deleteData,
    reset,
  };
} 