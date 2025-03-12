import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Search } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { libraryService } from '@/services/libraryService';

interface LibrarySelectionStepProps {
  onSelect: (library: any) => void;
  onContinue: () => void;
  selectedLibrary: any;
}

const LibrarySelectionStep: React.FC<LibrarySelectionStepProps> = ({ 
  onSelect, 
  onContinue,
  selectedLibrary
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  
  const { data: searchResults, isLoading } = useQuery({
    queryKey: ['librarySearch', searchQuery],
    queryFn: () => libraryService.searchLibraries({ query: searchQuery, limit: 10 }),
    enabled: searchQuery.length > 2
  });
  
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    // Search is handled by the useQuery hook
  };
  
  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Select Your Library</h2>
      <p className="text-gray-600 mb-6">
        Search for your library by name, city, or state to get started.
        This will be your primary library for the dashboard.
      </p>
      
      <form onSubmit={handleSearch} className="mb-6">
        <div className="relative">
          <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
            <Search className="h-5 w-5 text-gray-400" />
          </div>
          <Input
            type="text"
            placeholder="Search libraries..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
      </form>
      
      {isLoading && (
        <div className="flex justify-center my-8">
          <LoadingSpinner />
        </div>
      )}
      
      {searchResults && searchResults.libraries && (
        <div className="mb-6">
          <h3 className="text-lg font-medium mb-2">Search Results</h3>
          <div className="border rounded-md overflow-hidden">
            {searchResults.libraries.length === 0 ? (
              <div className="p-4 text-gray-500 text-center">
                No libraries found matching your search
              </div>
            ) : (
              <ul className="divide-y divide-gray-200">
                {searchResults.libraries.map((library) => (
                  <li key={library.id}>
                    <button
                      type="button"
                      onClick={() => onSelect(library)}
                      className={`w-full text-left px-4 py-3 hover:bg-gray-50 ${
                        selectedLibrary?.id === library.id ? 'bg-blue-50' : ''
                      }`}
                    >
                      <div className="font-medium">{library.name}</div>
                      <div className="text-sm text-gray-500">
                        {[
                          library.location?.city,
                          library.location?.state
                        ].filter(Boolean).join(', ')}
                      </div>
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}
      
      {selectedLibrary && (
        <div className="bg-blue-50 border border-blue-200 rounded-md p-4 mb-6">
          <h3 className="text-lg font-medium mb-2">Selected Library</h3>
          <div className="font-medium">{selectedLibrary.name}</div>
          <div className="text-sm text-gray-600">
            {[
              selectedLibrary.location?.address,
              selectedLibrary.location?.city,
              selectedLibrary.location?.state,
              selectedLibrary.location?.zip_code
            ].filter(Boolean).join(', ')}
          </div>
        </div>
      )}
      
      <div className="flex justify-end">
        <Button
          onClick={onContinue}
          disabled={!selectedLibrary}
          className="px-6 py-2"
        >
          Continue
        </Button>
      </div>
    </div>
  );
};

export default LibrarySelectionStep; 