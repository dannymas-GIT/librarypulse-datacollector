import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Search, Loader2, X, Plus } from 'lucide-react';

import { libraryConfigService, LibrarySearchResult, LibraryConfigCreate } from '../../services/libraryConfigService';

interface ComparisonLibrariesStepProps {
  formData: Partial<LibraryConfigCreate>;
  updateFormData: (data: Partial<LibraryConfigCreate>) => void;
  onNext: () => void;
  onBack: () => void;
}

const ComparisonLibrariesStep: React.FC<ComparisonLibrariesStepProps> = ({ 
  formData, 
  updateFormData,
  onNext,
  onBack
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedLibraries, setSelectedLibraries] = useState<LibrarySearchResult[]>(
    formData.comparison_libraries || []
  );
  
  // Search libraries query
  const { 
    data: searchResults, 
    isLoading: isSearching,
    refetch: searchLibraries,
    isFetching
  } = useQuery({
    queryKey: ['comparisonLibrarySearch', searchQuery],
    queryFn: () => libraryConfigService.searchLibraries(searchQuery),
    enabled: searchQuery.length >= 3, // Only search when at least 3 characters entered
  });
  
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };
  
  const handleLibrarySelect = (library: LibrarySearchResult) => {
    // Don't allow selecting the home library as a comparison library
    if (library.id === formData.library_id) {
      alert('You cannot select your home library as a comparison library.');
      return;
    }
    
    // Don't allow duplicates
    if (selectedLibraries.some(lib => lib.id === library.id)) {
      alert('This library is already in your comparison list.');
      return;
    }
    
    // Limit to 2 comparison libraries
    if (selectedLibraries.length >= 2) {
      alert('You can select a maximum of 2 comparison libraries.');
      return;
    }
    
    const updatedLibraries = [...selectedLibraries, library];
    setSelectedLibraries(updatedLibraries);
    updateFormData({
      comparison_libraries: updatedLibraries
    });
    
    // Clear search
    setSearchQuery('');
  };
  
  const handleRemoveLibrary = (libraryId: string) => {
    const updatedLibraries = selectedLibraries.filter(lib => lib.id !== libraryId);
    setSelectedLibraries(updatedLibraries);
    updateFormData({
      comparison_libraries: updatedLibraries
    });
  };
  
  const handleContinue = () => {
    onNext();
  };
  
  // Filter out the home library from search results
  const filteredSearchResults = searchResults?.filter(
    (lib: LibrarySearchResult) => lib.id !== formData.library_id
  );
  
  return (
    <div>
      <h2 className="text-2xl font-semibold mb-4">Select Comparison Libraries</h2>
      <p className="text-gray-600 mb-6">
        <strong>Select up to 2 libraries</strong> to compare with your home library. This will help you benchmark your library's performance against similar libraries.
      </p>
      
      {/* Selected home library info */}
      <div className="mb-6 p-4 bg-blue-50 rounded-lg">
        <h3 className="text-lg font-medium mb-2">Your Home Library</h3>
        <div className="font-medium">{formData.library_name}</div>
        <div className="text-sm text-gray-500">ID: {formData.library_id}</div>
      </div>
      
      {/* Selected comparison libraries */}
      <div className="mb-6">
        <h3 className="text-lg font-medium mb-2">Selected Comparison Libraries ({selectedLibraries.length}/2)</h3>
        
        {selectedLibraries.length === 0 ? (
          <div className="p-4 border rounded-lg text-gray-500">
            No comparison libraries selected yet. Search below to add libraries.
          </div>
        ) : (
          <div className="border rounded-lg divide-y">
            {selectedLibraries.map(library => (
              <div 
                key={library.id}
                className="p-4 flex justify-between items-center"
              >
                <div>
                  <div className="font-medium">{library.name}</div>
                  <div className="text-sm text-gray-500">
                    {library.city}, {library.state} - ID: {library.id}
                  </div>
                </div>
                <button
                  className="text-red-500 hover:text-red-700"
                  onClick={() => handleRemoveLibrary(library.id)}
                  aria-label="Remove library"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
      
      {/* Search heading */}
      <h3 className="text-lg font-medium mb-2">Search for Libraries to Compare</h3>
      
      {/* Search input */}
      <div className="relative mb-6">
        <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
          <Search className="w-5 h-5 text-gray-500" />
        </div>
        <input
          type="search"
          className="block w-full p-4 pl-10 text-sm text-gray-900 border border-gray-300 rounded-lg bg-white focus:ring-blue-500 focus:border-blue-500"
          placeholder="Enter library name, city, or ID (minimum 3 characters)"
          value={searchQuery}
          onChange={handleSearchChange}
          disabled={selectedLibraries.length >= 2}
        />
        {isFetching && (
          <div className="absolute inset-y-0 right-0 flex items-center pr-3">
            <Loader2 className="w-5 h-5 text-gray-400 animate-spin" />
          </div>
        )}
      </div>
      
      {selectedLibraries.length >= 2 && (
        <div className="mb-6 p-4 bg-blue-50 rounded-lg text-blue-800">
          You have selected the maximum of 2 comparison libraries. Remove one to select a different library.
        </div>
      )}
      
      {/* Search results */}
      {filteredSearchResults && filteredSearchResults.length > 0 && searchQuery.length >= 3 && selectedLibraries.length < 2 && (
        <div className="mb-6">
          <h3 className="text-lg font-medium mb-2">Search Results</h3>
          <div className="border rounded-lg divide-y max-h-64 overflow-y-auto">
            {filteredSearchResults.map((library: LibrarySearchResult) => (
              <div 
                key={library.id}
                className="p-4 hover:bg-gray-50 cursor-pointer flex justify-between items-center"
                onClick={() => handleLibrarySelect(library)}
              >
                <div>
                  <div className="font-medium">{library.name}</div>
                  <div className="text-sm text-gray-500">
                    {library.city}, {library.state} - ID: {library.id}
                  </div>
                </div>
                <Plus className="w-5 h-5 text-blue-500" />
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* No results message */}
      {searchQuery.length >= 3 && (!filteredSearchResults || filteredSearchResults.length === 0) && !isFetching && selectedLibraries.length < 2 && (
        <div className="mb-6 p-4 text-amber-800 bg-amber-50 rounded-lg">
          No libraries found matching "{searchQuery}". 
          Please try a different search term.
        </div>
      )}
      
      {/* Navigation buttons */}
      <div className="mt-8 flex justify-between">
        <button
          className="px-6 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300"
          onClick={onBack}
        >
          Back
        </button>
        <button
          className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          onClick={handleContinue}
        >
          Continue {selectedLibraries.length > 0 ? `with ${selectedLibraries.length} comparison ${selectedLibraries.length === 1 ? 'library' : 'libraries'}` : ''}
        </button>
      </div>
    </div>
  );
};

export default ComparisonLibrariesStep; 