import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Search, Plus, X } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { LoadingSpinner } from '@/components/ui/LoadingSpinner';
import { libraryService } from '@/services/libraryService';

interface ComparisonLibrariesStepProps {
  primaryLibrary: any;
  selectedLibraries: any[];
  onSelect: (libraries: any[]) => void;
  onContinue: () => void;
  onBack: () => void;
}

const ComparisonLibrariesStep: React.FC<ComparisonLibrariesStepProps> = ({
  primaryLibrary,
  selectedLibraries,
  onSelect,
  onContinue,
  onBack
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  
  const { data: searchResults, isLoading } = useQuery({
    queryKey: ['librarySearch', searchQuery],
    queryFn: () => libraryService.searchLibraries({ query: searchQuery, limit: 10 }),
    enabled: searchQuery.length > 2
  });
  
  const handleSearch = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    // Search is handled by the useQuery hook
  };
  
  const addLibrary = (library: any) => {
    if (!selectedLibraries.some(lib => lib.id === library.id) && 
        library.id !== primaryLibrary.id) {
      onSelect([...selectedLibraries, library]);
    }
  };
  
  const removeLibrary = (libraryId: string) => {
    onSelect(selectedLibraries.filter(lib => lib.id !== libraryId));
  };
  
  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Select Comparison Libraries</h2>
      <p className="text-gray-600 mb-6">
        Select libraries to compare with your primary library.
        You can add up to 5 libraries for comparison.
      </p>
      
      <form onSubmit={handleSearch} className="mb-6">
        <div className="relative">
          <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
            <Search className="h-5 w-5 text-gray-400" />
          </div>
          <Input
            type="text"
            placeholder="Search libraries to compare..."
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
      
      {searchResults && searchResults.libraries && searchQuery.length > 2 && (
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
                      onClick={() => addLibrary(library)}
                      className="w-full text-left px-4 py-3 hover:bg-gray-50 flex justify-between items-center"
                      disabled={
                        selectedLibraries.some(lib => lib.id === library.id) ||
                        library.id === primaryLibrary.id ||
                        selectedLibraries.length >= 5
                      }
                    >
                      <div>
                        <div className="font-medium">{library.name}</div>
                        <div className="text-sm text-gray-500">
                          {[
                            library.location?.city,
                            library.location?.state
                          ].filter(Boolean).join(', ')}
                        </div>
                      </div>
                      <Plus className="h-5 w-5 text-gray-400" />
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}
      
      <div className="mb-6">
        <h3 className="text-lg font-medium mb-2">Selected Libraries</h3>
        <div className="bg-blue-50 border border-blue-200 rounded-md p-4 mb-4">
          <div className="font-medium">{primaryLibrary.name} (Primary)</div>
          <div className="text-sm text-gray-600">
            {[
              primaryLibrary.location?.city,
              primaryLibrary.location?.state
            ].filter(Boolean).join(', ')}
          </div>
        </div>
        
        {selectedLibraries.length === 0 ? (
          <div className="text-gray-500 text-center border rounded-md p-4">
            No comparison libraries selected
          </div>
        ) : (
          <ul className="space-y-2">
            {selectedLibraries.map((library) => (
              <li key={library.id} className="flex justify-between items-center border rounded-md p-3">
                <div>
                  <div className="font-medium">{library.name}</div>
                  <div className="text-sm text-gray-500">
                    {[
                      library.location?.city,
                      library.location?.state
                    ].filter(Boolean).join(', ')}
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => removeLibrary(library.id)}
                  className="text-gray-400 hover:text-red-500"
                >
                  <X className="h-5 w-5" />
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
      
      <div className="flex justify-between">
        <Button onClick={onBack} variant="outline" className="px-6 py-2">
          Back
        </Button>
        <Button onClick={onContinue} className="px-6 py-2">
          Continue
        </Button>
      </div>
    </div>
  );
};

export default ComparisonLibrariesStep; 