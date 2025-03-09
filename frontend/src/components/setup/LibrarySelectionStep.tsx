import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Search, Loader2 } from 'lucide-react';

import { libraryConfigService, LibrarySearchResult, LibraryConfigCreate } from '../../services/libraryConfigService';

interface LibrarySelectionStepProps {
  formData: Partial<LibraryConfigCreate>;
  updateFormData: (data: Partial<LibraryConfigCreate>) => void;
  onNext: () => void;
}

const LibrarySelectionStep: React.FC<LibrarySelectionStepProps> = ({ 
  formData, 
  updateFormData,
  onNext 
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedLibrary, setSelectedLibrary] = useState<LibrarySearchResult | null>(
    formData.library_id ? { 
      id: formData.library_id, 
      name: formData.library_name ?? '', 
      city: '', 
      state: '' 
    } : null
  );
  
  // Search libraries query
  const { 
    data: searchResults, 
    isLoading: isSearching,
    refetch: searchLibraries,
    isFetching
  } = useQuery({
    queryKey: ['librarySearch', searchQuery],
    queryFn: () => libraryConfigService.searchLibraries(searchQuery),
    enabled: searchQuery.length >= 3, // Only search when at least 3 characters entered
  });
  
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };
  
  const handleLibrarySelect = (library: LibrarySearchResult) => {
    setSelectedLibrary(library);
    updateFormData({
      library_id: library.id,
      library_name: library.name
    });
  };
  
  const handleContinue = () => {
    if (!selectedLibrary) {
      alert('Please select a library to continue.');
      return;
    }
    
    onNext();
  };
  
  return (
    <div>
      <h2 className="text-2xl font-semibold mb-4">Select Your Library</h2>
      <p className="text-gray-600 mb-6">
        Search for and select your library. The application will be configured to focus on your library's data.
      </p>
      
      {/* Search input */}
      <div className="relative mb-6">
        <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
          <Search className="w-5 h-5 text-gray-500" />
        </div>
        <input
          type="search"
          className="block w-full p-4 pl-10 text-sm text-gray-900 border border-gray-300 rounded-lg bg-white focus:ring-blue-500 focus:border-blue-500"
          placeholder="Enter library name or ID (minimum 3 characters)"
          value={searchQuery}
          onChange={handleSearchChange}
        />
        {isFetching && (
          <div className="absolute inset-y-0 right-0 flex items-center pr-3">
            <Loader2 className="w-5 h-5 text-gray-400 animate-spin" />
          </div>
        )}
      </div>
      
      {/* Search results */}
      {searchResults && searchResults.length > 0 && !selectedLibrary && (
        <div className="mb-6">
          <h3 className="text-lg font-medium mb-2">Search Results</h3>
          <div className="border rounded-lg divide-y">
            {searchResults.map(library => (
              <div 
                key={library.id}
                className="p-4 hover:bg-gray-50 cursor-pointer"
                onClick={() => handleLibrarySelect(library)}
              >
                <div className="font-medium">{library.name}</div>
                <div className="text-sm text-gray-500">
                  {library.city}, {library.state} - ID: {library.id}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* No results message */}
      {searchQuery.length >= 3 && searchResults && searchResults.length === 0 && !isFetching && (
        <div className="mb-6 p-4 text-amber-800 bg-amber-50 rounded-lg">
          No libraries found matching "{searchQuery}". 
          Please try a different search term or contact support if you believe your library should be in the system.
        </div>
      )}
      
      {/* Selected library */}
      {selectedLibrary && (
        <div className="mb-6">
          <h3 className="text-lg font-medium mb-2">Selected Library</h3>
          <div className="border rounded-lg p-4 bg-blue-50">
            <div className="font-medium">{selectedLibrary.name}</div>
            {(selectedLibrary.city || selectedLibrary.state) && (
              <div className="text-sm text-gray-600">
                {selectedLibrary.city}, {selectedLibrary.state}
              </div>
            )}
            <div className="text-sm text-gray-500">ID: {selectedLibrary.id}</div>
            
            <button
              className="mt-2 text-sm text-blue-600 hover:text-blue-800"
              onClick={() => setSelectedLibrary(null)}
            >
              Change Library
            </button>
          </div>
        </div>
      )}
      
      {/* Continue button */}
      <div className="mt-8 flex justify-end">
        <button
          className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed"
          disabled={!selectedLibrary}
          onClick={handleContinue}
        >
          Continue
        </button>
      </div>
    </div>
  );
};

export default LibrarySelectionStep; 