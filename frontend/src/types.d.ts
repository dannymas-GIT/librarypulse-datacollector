/// <reference types="react" />
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

declare module '@tanstack/react-query' {
  interface QueryKey extends ReadonlyArray<unknown> {}
  
  interface QueryFunction<T = unknown, TQueryKey extends QueryKey = QueryKey> {
    (context: QueryFunctionContext<TQueryKey>): T | Promise<T>;
  }

  interface UseMutationOptions<TData = unknown, TError = unknown, TVariables = void> {
    mutationFn?: (variables: TVariables) => Promise<TData>;
    onMutate?: (variables: TVariables) => Promise<unknown> | unknown;
    onError?: (error: TError, variables: TVariables, context: unknown) => Promise<unknown> | unknown;
    onSuccess?: (data: TData, variables: TVariables, context: unknown) => Promise<unknown> | unknown;
    onSettled?: (data: TData | undefined, error: TError | null, variables: TVariables, context: unknown) => Promise<unknown> | unknown;
  }
} 