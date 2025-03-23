/// <reference types="react" />

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
  export const AlertCircle: React.FC<any>;
  export const AlertTriangle: React.FC<any>;
  export const ArrowDown: React.FC<any>;
  export const ArrowLeft: React.FC<any>;
  export const ArrowRight: React.FC<any>;
  export const ArrowUp: React.FC<any>;
  export const ArrowUpDown: React.FC<any>;
  export const BarChart: React.FC<any>;
  export const BarChart2: React.FC<any>;
  export const BarChart3: React.FC<any>;
  export const BarChart4: React.FC<any>;
  export const Bell: React.FC<any>;
  export const BookOpen: React.FC<any>;
  export const BookText: React.FC<any>;
  export const Calendar: React.FC<any>;
  export const Check: React.FC<any>;
  export const CheckCircle: React.FC<any>;
  export const CheckCircle2: React.FC<any>;
  export const ChevronDown: React.FC<any>;
  export const ChevronLeft: React.FC<any>;
  export const ChevronRight: React.FC<any>;
  export const ChevronUp: React.FC<any>;
  export const Clock: React.FC<any>;
  export const Database: React.FC<any>;
  export const DollarSign: React.FC<any>;
  export const Download: React.FC<any>;
  export const Eye: React.FC<any>;
  export const EyeOff: React.FC<any>;
  export const FileBox: React.FC<any>;
  export const FileText: React.FC<any>;
  export const Filter: React.FC<any>;
  export const Globe: React.FC<any>;
  export const HelpCircle: React.FC<any>;
  export const Home: React.FC<any>;
  export const Info: React.FC<any>;
  export const Layers: React.FC<any>;
  export const Library: React.FC<any>;
  export const LineChart: React.FC<any>;
  export const Loader: React.FC<any>;
  export const Loader2: React.FC<any>;
  export const LogOut: React.FC<any>;
  export const Mail: React.FC<any>;
  export const MapPin: React.FC<any>;
  export const Menu: React.FC<any>;
  export const Phone: React.FC<any>;
  export const Plus: React.FC<any>;
  export const RefreshCw: React.FC<any>;
  export const Search: React.FC<any>;
  export const Settings: React.FC<any>;
  export const TrendingUp: React.FC<any>;
  export const Upload: React.FC<any>;
  export const User: React.FC<any>;
  export const Users: React.FC<any>;
  export const X: React.FC<any>;
  export const XCircle: React.FC<any>;
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