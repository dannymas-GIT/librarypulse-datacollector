import { get, post, put, del } from '@/utils/api';

export interface Library {
  id: number;
  fscs_id: string;
  name: string;
  address: string;
  city: string;
  state: string;
  zip_code: string;
  phone: string;
  type: string;
  administrative_structure: string;
  service_area: string;
  population_served: number;
  central_library: boolean;
  branches: number;
  bookmobiles: number;
  year_founded: number | null;
  director_name: string | null;
  director_email: string | null;
  website: string | null;
  total_staff: number | null;
  total_librarians: number | null;
  total_mls_librarians: number | null;
  created_at: string;
  updated_at: string;
}

export interface LibraryOutlet {
  id: number;
  library_id: number;
  fscs_seq: string;
  name: string;
  address: string;
  city: string;
  state: string;
  zip_code: string;
  phone: string;
  outlet_type: string;
  square_footage: number | null;
  created_at: string;
  updated_at: string;
}

export interface LibraryFilters {
  state?: string;
  city?: string;
  type?: string;
  population_min?: number;
  population_max?: number;
  search?: string;
  page?: number;
  limit?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

// Mock data for development until the API is ready
const mockLibraries: Library[] = Array.from({ length: 50 }, (_, i) => ({
  id: i + 1,
  fscs_id: `${['AL', 'AK', 'AZ', 'CA', 'CO', 'FL', 'GA', 'IL', 'NY', 'TX'][i % 10]}${String(i + 1).padStart(5, '0')}`,
  name: `Sample Library ${i + 1}`,
  address: `${Math.floor(Math.random() * 9000) + 1000} Main St`,
  city: `City ${i + 1}`,
  state: ['AL', 'AK', 'AZ', 'CA', 'CO', 'FL', 'GA', 'IL', 'NY', 'TX'][i % 10],
  zip_code: `${Math.floor(Math.random() * 90000) + 10000}`,
  phone: `${Math.floor(Math.random() * 900) + 100}-${Math.floor(Math.random() * 900) + 100}-${Math.floor(Math.random() * 9000) + 1000}`,
  type: ['Public', 'Academic', 'School', 'Special'][i % 4],
  administrative_structure: ['Municipal', 'County', 'Non-profit', 'State'][i % 4],
  service_area: `${['City', 'County', 'District', 'Region'][i % 4]} ${i + 1}`,
  population_served: Math.floor(Math.random() * 100000) + 5000,
  central_library: i % 5 !== 0,
  branches: Math.floor(Math.random() * 5),
  bookmobiles: Math.floor(Math.random() * 2),
  year_founded: 1900 + Math.floor(Math.random() * 120),
  director_name: `Director ${i + 1}`,
  director_email: `director${i + 1}@library${i + 1}.org`,
  website: `https://library${i + 1}.org`,
  total_staff: Math.floor(Math.random() * 50) + 5,
  total_librarians: Math.floor(Math.random() * 20) + 2,
  total_mls_librarians: Math.floor(Math.random() * 10) + 1,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
}));

// Get a paginated list of libraries with optional filters
export const getLibraries = (filters: LibraryFilters = {}): Promise<PaginatedResponse<Library>> => {
  // For development, use mock data
  return new Promise((resolve) => {
    setTimeout(() => {
      const { page = 1, limit = 10, search = '', state, type, population_min, population_max } = filters;
      
      let filtered = [...mockLibraries];
      
      // Apply filters
      if (search) {
        const searchLower = search.toLowerCase();
        filtered = filtered.filter(lib => 
          lib.name.toLowerCase().includes(searchLower) || 
          lib.city.toLowerCase().includes(searchLower) ||
          lib.fscs_id.toLowerCase().includes(searchLower)
        );
      }
      
      if (state) {
        filtered = filtered.filter(lib => lib.state === state);
      }
      
      if (type) {
        filtered = filtered.filter(lib => lib.type === type);
      }
      
      if (population_min !== undefined) {
        filtered = filtered.filter(lib => lib.population_served >= population_min);
      }
      
      if (population_max !== undefined) {
        filtered = filtered.filter(lib => lib.population_served <= population_max);
      }
      
      // Calculate pagination
      const total = filtered.length;
      const pages = Math.ceil(total / limit);
      const startIndex = (page - 1) * limit;
      const endIndex = startIndex + limit;
      const items = filtered.slice(startIndex, endIndex);
      
      resolve({
        items,
        total,
        page,
        limit,
        pages
      });
    }, 500); // Simulate network delay
  });
};

// Get a single library by ID
export const getLibrary = (id: number): Promise<Library> => {
  // For development, use mock data
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      const library = mockLibraries.find(lib => lib.id === id);
      if (library) {
        resolve(library);
      } else {
        reject(new Error(`Library with ID ${id} not found`));
      }
    }, 300); // Simulate network delay
  });
};

// Get outlets for a library
export const getLibraryOutlets = (libraryId: number): Promise<LibraryOutlet[]> => {
  // For development, use mock data
  return new Promise((resolve) => {
    setTimeout(() => {
      const library = mockLibraries.find(lib => lib.id === libraryId);
      if (!library) {
        resolve([]);
        return;
      }
      
      const outlets: LibraryOutlet[] = [];
      
      // Add central library as an outlet if it exists
      if (library.central_library) {
        outlets.push({
          id: libraryId * 100,
          library_id: libraryId,
          fscs_seq: '01',
          name: library.name,
          address: library.address,
          city: library.city,
          state: library.state,
          zip_code: library.zip_code,
          phone: library.phone,
          outlet_type: 'Central',
          square_footage: Math.floor(Math.random() * 50000) + 10000,
          created_at: library.created_at,
          updated_at: library.updated_at
        });
      }
      
      // Add branch libraries
      for (let i = 0; i < library.branches; i++) {
        outlets.push({
          id: libraryId * 100 + i + 1,
          library_id: libraryId,
          fscs_seq: `${i + 2}`.padStart(2, '0'),
          name: `${library.name} - Branch ${i + 1}`,
          address: `${Math.floor(Math.random() * 9000) + 1000} Branch St`,
          city: library.city,
          state: library.state,
          zip_code: library.zip_code,
          phone: `${Math.floor(Math.random() * 900) + 100}-${Math.floor(Math.random() * 900) + 100}-${Math.floor(Math.random() * 9000) + 1000}`,
          outlet_type: 'Branch',
          square_footage: Math.floor(Math.random() * 20000) + 5000,
          created_at: library.created_at,
          updated_at: library.updated_at
        });
      }
      
      resolve(outlets);
    }, 300); // Simulate network delay
  });
};

// Get statistics for a library
export const getLibraryStatistics = (libraryId: number, year?: number): Promise<any> => {
  // For development, return mock data
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        visits: Math.floor(Math.random() * 100000) + 10000,
        circulation: Math.floor(Math.random() * 200000) + 20000,
        programs: Math.floor(Math.random() * 500) + 50,
        program_attendance: Math.floor(Math.random() * 10000) + 1000,
        computer_uses: Math.floor(Math.random() * 20000) + 2000,
        wifi_uses: Math.floor(Math.random() * 30000) + 3000,
        reference_transactions: Math.floor(Math.random() * 5000) + 500,
        year: year || 2021
      });
    }, 300); // Simulate network delay
  });
};

// Get trends for a library
export const getLibraryTrends = (
  libraryId: number, 
  metric: string, 
  startYear?: number, 
  endYear?: number
): Promise<any> => {
  // For development, return mock data
  return new Promise((resolve) => {
    setTimeout(() => {
      const start = startYear || 2017;
      const end = endYear || 2021;
      const years = Array.from({ length: end - start + 1 }, (_, i) => start + i);
      
      const data = years.map(year => ({
        year,
        value: Math.floor(Math.random() * 100000) + 10000
      }));
      
      resolve({
        metric,
        data
      });
    }, 300); // Simulate network delay
  });
};

// Compare libraries
export const compareLibraries = (
  libraryIds: number[], 
  metrics: string[], 
  year?: number
): Promise<any> => {
  // For development, return mock data
  return new Promise((resolve) => {
    setTimeout(() => {
      const libraries = libraryIds.map(id => {
        const library = mockLibraries.find(lib => lib.id === id);
        if (!library) return null;
        
        const metricData: Record<string, number> = {};
        metrics.forEach(metric => {
          metricData[metric] = Math.floor(Math.random() * 100000) + 1000;
        });
        
        return {
          id,
          name: library.name,
          metrics: metricData
        };
      }).filter(Boolean);
      
      resolve({
        year: year || 2021,
        libraries
      });
    }, 500); // Simulate network delay
  });
};

// Get available years for data
export const getAvailableYears = (): Promise<number[]> => {
  // For development, return mock data
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve([2017, 2018, 2019, 2020, 2021]);
    }, 200); // Simulate network delay
  });
};

// Get available metrics for comparison
export const getAvailableMetrics = (): Promise<{ id: string; name: string; category: string }[]> => {
  // For development, return mock data
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve([
        { id: 'visits', name: 'Library Visits', category: 'Usage' },
        { id: 'circulation', name: 'Total Circulation', category: 'Usage' },
        { id: 'programs', name: 'Programs Offered', category: 'Programs' },
        { id: 'program_attendance', name: 'Program Attendance', category: 'Programs' },
        { id: 'computer_uses', name: 'Computer Uses', category: 'Technology' },
        { id: 'wifi_uses', name: 'WiFi Uses', category: 'Technology' },
        { id: 'reference_transactions', name: 'Reference Transactions', category: 'Services' },
        { id: 'total_staff', name: 'Total Staff', category: 'Staffing' },
        { id: 'total_librarians', name: 'Total Librarians', category: 'Staffing' },
        { id: 'total_income', name: 'Total Income', category: 'Financial' },
        { id: 'total_expenditures', name: 'Total Expenditures', category: 'Financial' },
      ]);
    }, 200); // Simulate network delay
  });
}; 