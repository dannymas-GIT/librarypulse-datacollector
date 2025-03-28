/// <reference types="react" />

import * as React from 'react';

declare global {
  namespace JSX {
    interface IntrinsicElements {
      div: React.DetailedHTMLProps<React.HTMLAttributes<HTMLDivElement>, HTMLDivElement>;
      span: React.DetailedHTMLProps<React.HTMLAttributes<HTMLSpanElement>, HTMLSpanElement>;
      p: React.DetailedHTMLProps<React.HTMLAttributes<HTMLParagraphElement>, HTMLParagraphElement>;
      // Add other HTML elements as needed
    }
  }
}

// Allow any element name in JSX
declare namespace JSX {
  interface IntrinsicElements {
    [elemName: string]: any;
  }
}

// DOM element types
interface HTMLElement {}
interface HTMLDivElement extends HTMLElement {}
interface HTMLInputElement extends HTMLElement {}
interface HTMLSelectElement extends HTMLElement {}
interface HTMLButtonElement extends HTMLElement {}
interface Element {}
interface Node {}
interface DocumentFragment {}
interface KeyboardEvent {
  key: string;
}
interface MouseEvent {
  target: any;
}

// Declare modules for libraries without TypeScript definitions
declare module 'react' {
  export interface ReactElement<P = any, T extends string | JSXElementConstructor<any> = string | JSXElementConstructor<any>> {
    type: T;
    props: P;
    key: Key | null;
  }

  export type ReactNode = 
    | ReactElement 
    | string 
    | number 
    | Iterable<ReactNode> 
    | ReactPortal 
    | boolean 
    | null 
    | undefined;

  export type FC<P = {}> = FunctionComponent<P>;
  
  export interface FunctionComponent<P = {}> {
    (props: P, context?: any): ReactElement<any, any> | null;
    displayName?: string;
  }

  export type Key = string | number;

  export type JSXElementConstructor<P> = 
    | ((props: P) => ReactElement<any, any> | null)
    | (new (props: P) => Component<any, any>);

  export interface Component<P = {}, S = {}> {
    render(): ReactNode;
    props: Readonly<P>;
    state: Readonly<S>;
    setState(state: S | ((prevState: Readonly<S>, props: Readonly<P>) => S | null)): void;
  }

  export interface ReactPortal extends ReactElement {
    key: Key | null;
    children: ReactNode;
  }

  export interface HTMLAttributes<T> {
    className?: string;
    style?: any;
    id?: string;
    onClick?: (event: any) => void;
    onMouseOver?: (event: any) => void;
    onMouseOut?: (event: any) => void;
    onKeyDown?: (event: any) => void;
    onKeyUp?: (event: any) => void;
    onFocus?: (event: any) => void;
    onBlur?: (event: any) => void;
    [key: string]: any;
  }

  export interface ButtonHTMLAttributes<T> extends HTMLAttributes<T> {
    type?: 'button' | 'submit' | 'reset';
    disabled?: boolean;
    form?: string;
    formAction?: string;
    formEncType?: string;
    formMethod?: string;
    formNoValidate?: boolean;
    formTarget?: string;
    name?: string;
    value?: string | string[] | number;
  }

  export interface InputHTMLAttributes<T> extends HTMLAttributes<T> {
    accept?: string;
    alt?: string;
    autoComplete?: string;
    autoFocus?: boolean;
    checked?: boolean;
    disabled?: boolean;
    form?: string;
    list?: string;
    max?: number | string;
    maxLength?: number;
    min?: number | string;
    minLength?: number;
    multiple?: boolean;
    name?: string;
    pattern?: string;
    placeholder?: string;
    readOnly?: boolean;
    required?: boolean;
    size?: number;
    src?: string;
    step?: number | string;
    type?: string;
    value?: string | string[] | number;
  }

  export interface SelectHTMLAttributes<T> extends HTMLAttributes<T> {
    autoComplete?: string;
    autoFocus?: boolean;
    disabled?: boolean;
    form?: string;
    multiple?: boolean;
    name?: string;
    required?: boolean;
    size?: number;
    value?: string | string[] | number;
  }

  export interface ChangeEvent<T = Element> {
    target: T;
    currentTarget: T;
    type: string;
  }

  export function useState<T>(initialState: T | (() => T)): [T, (newState: T | ((prevState: T) => T)) => void];
  export function useEffect(effect: () => void | (() => void), deps?: any[]): void;
  export function useContext<T>(context: React.Context<T>): T;
  export function useReducer<S, A>(reducer: (state: S, action: A) => S, initialState: S): [S, (action: A) => void];
  export function useCallback<T extends (...args: any[]) => any>(callback: T, deps: any[]): T;
  export function useMemo<T>(factory: () => T, deps: any[]): T;
  export function useRef<T>(initialValue: T | null): { current: T | null };
  export function forwardRef<T, P = {}>(render: (props: P, ref: React.Ref<T>) => React.ReactElement | null): (props: P & { ref?: React.Ref<T> }) => React.ReactElement | null;

  export type Ref<T> = React.RefObject<T> | ((instance: T | null) => void) | null;
  export interface RefObject<T> {
    readonly current: T | null;
  }
  export function createContext<T>(defaultValue: T): React.Context<T>;
  export interface Context<T> {
    Provider: React.Provider<T>;
    Consumer: React.Consumer<T>;
    displayName?: string;
  }
  export interface Provider<T> {
    (props: { value: T; children?: React.ReactNode }): React.ReactElement | null;
  }
  export interface Consumer<T> {
    (props: { children: (value: T) => React.ReactNode }): React.ReactElement | null;
  }
}

// React JSX Runtime
declare module 'react/jsx-runtime' {
  export namespace JSX {
    interface Element extends React.ReactElement<any, any> {}
  }
  export function jsx(
    type: React.ElementType,
    props: any,
    key?: React.Key
  ): JSX.Element;
  export function jsxs(
    type: React.ElementType,
    props: any,
    key?: React.Key
  ): JSX.Element;
}

declare module 'react-dom/client' {
  export function createRoot(container: Element | DocumentFragment): {
    render(element: React.ReactNode): void;
    unmount(): void;
  };
}

declare module 'react-router-dom' {
  export function BrowserRouter(props: any): JSX.Element;
  export function Routes(props: any): JSX.Element;
  export function Route(props: any): JSX.Element;
  export function Link(props: any): JSX.Element;
  export function NavLink(props: any): JSX.Element;
  export function Navigate(props: { to: string; replace?: boolean; state?: any }): JSX.Element;
  export function Outlet(props: any): JSX.Element;
  export function useParams(): Record<string, string>;
  export function useNavigate(): (path: string, options?: { replace?: boolean; state?: any }) => void;
  export function useLocation(): { pathname: string; search: string; hash: string; state: any };
}

declare module '@tanstack/react-query' {
  export function QueryClient(options?: any): any;
  export function QueryClientProvider(props: any): JSX.Element;
  export function useQuery(options: any): any;
  
  // Add useMutation
  export function useMutation(options: {
    mutationFn: (variables: any) => Promise<any>;
    onSuccess?: (data: any, variables: any, context: any) => void;
    onError?: (error: any, variables: any, context: any) => void;
    onSettled?: (data: any, error: any, variables: any, context: any) => void;
  }): {
    mutate: (variables: any) => void;
    mutateAsync: (variables: any) => Promise<any>;
    isLoading: boolean;
    isSuccess: boolean;
    isError: boolean;
    data: any;
    error: any;
    reset: () => void;
  };
  
  // Add useQueryClient
  export function useQueryClient(): {
    invalidateQueries: (options: { queryKey: any[] }) => Promise<void>;
    setQueryData: (queryKey: any[], updater: any) => void;
    getQueryData: (queryKey: any[]) => any;
    refetchQueries: (options: { queryKey: any[] }) => Promise<void>;
  };
}

declare module '@tanstack/react-query-devtools' {
  export * from '@tanstack/react-query-devtools';
}

declare module 'lucide-react' {
  export interface LucideProps extends React.SVGAttributes<SVGElement> {
    size?: number | string;
    absoluteStrokeWidth?: boolean;
  }
  
  export const PieChart: React.FC<LucideProps>;
  export const BarChart: React.FC<LucideProps>;
  export const LineChart: React.FC<LucideProps>;
  export const BookOpen: React.FC<LucideProps>;
  export const TrendingUp: React.FC<LucideProps>;
  export const Users: React.FC<LucideProps>;
  export const Database: React.FC<LucideProps>;
  export const ArrowRight: React.FC<LucideProps>;
}

declare module 'axios' {
  export interface AxiosRequestConfig {
    baseURL?: string;
    url?: string;
    method?: string;
    headers?: Record<string, string>;
    params?: any;
    data?: any;
    timeout?: number;
    withCredentials?: boolean;
  }

  export interface AxiosResponse<T = any> {
    data: T;
    status: number;
    statusText: string;
    headers: Record<string, string>;
    config: AxiosRequestConfig;
    request?: any;
  }

  export interface AxiosError<T = any> extends Error {
    config: AxiosRequestConfig;
    code?: string;
    request?: any;
    response?: AxiosResponse<T>;
    isAxiosError: boolean;
    toJSON: () => object;
  }

  export function create(config?: AxiosRequestConfig): any;
  export function isAxiosError(payload: any): payload is AxiosError;
}

// Module declarations for local imports
declare module '@/services/statsService' {
  export function getLibraryStats(): Promise<any>;
  export function getLibraryTrends(): Promise<any>;
}

// React namespace
declare namespace React {
  interface ReactNode {}
} 