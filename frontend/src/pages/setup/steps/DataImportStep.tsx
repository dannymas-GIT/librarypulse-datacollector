import React, { useState, useEffect } from 'react';
import { CheckCircle, XCircle, Loader } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import libraryDataService from '@/services/libraryDataService';

interface DataImportStepProps {
  primaryLibrary: any;
  comparisonLibraries: any[];
  onComplete: () => void;
  onBack: () => void;
}

type ImportStatus = 'pending' | 'importing' | 'success' | 'error';

const DataImportStep: React.FC<DataImportStepProps> = ({
  primaryLibrary,
  comparisonLibraries,
  onComplete,
  onBack
}) => {
  const [importStatus, setImportStatus] = useState<Record<string, ImportStatus>>({});
  const [isImporting, setIsImporting] = useState(false);
  
  // Initialize import status
  useEffect(() => {
    const initialStatus: Record<string, ImportStatus> = {
      [primaryLibrary.id]: 'pending'
    };
    
    comparisonLibraries.forEach(library => {
      initialStatus[library.id] = 'pending';
    });
    
    setImportStatus(initialStatus);
  }, [primaryLibrary, comparisonLibraries]);
  
  // Start import process
  const startImport = async () => {
    setIsImporting(true);
    
    // Save user preferences first
    await libraryDataService.saveUserPreferences({
      primaryLibraryId: primaryLibrary.id,
      comparisonLibraryIds: comparisonLibraries.map(lib => lib.id)
    });
    
    // Import primary library data
    await importLibraryData(primaryLibrary.id);
    
    // Import comparison libraries data
    for (const library of comparisonLibraries) {
      await importLibraryData(library.id);
    }
    
    setIsImporting(false);
  };
  
  // Import data for a single library
  const importLibraryData = async (libraryId: string) => {
    setImportStatus(prev => ({
      ...prev,
      [libraryId]: 'importing'
    }));
    
    try {
      // Simulate API call with delay
      await new Promise(resolve => setTimeout(resolve, 1500));
      const success = await libraryDataService.importLibraryData(libraryId);
      
      setImportStatus(prev => ({
        ...prev,
        [libraryId]: success ? 'success' : 'error'
      }));
      
      return success;
    } catch (error) {
      setImportStatus(prev => ({
        ...prev,
        [libraryId]: 'error'
      }));
      
      return false;
    }
  };
  
  // Check if all imports are complete
  const isImportComplete = () => {
    return Object.values(importStatus).every(status => 
      status === 'success' || status === 'error'
    );
  };
  
  // Check if import was successful
  const isImportSuccessful = () => {
    return importStatus[primaryLibrary.id] === 'success' && 
      Object.values(importStatus).filter(status => status === 'error').length === 0;
  };
  
  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Import Library Data</h2>
      <p className="text-gray-600 mb-6">
        We'll now import the data for your selected libraries.
        This may take a few moments.
      </p>
      
      <div className="mb-6">
        <h3 className="text-lg font-medium mb-2">Import Status</h3>
        <ul className="space-y-3">
          <li className="flex items-center justify-between border rounded-md p-3">
            <div>
              <div className="font-medium">{primaryLibrary.name} (Primary)</div>
              <div className="text-sm text-gray-500">
                {[
                  primaryLibrary.location?.city,
                  primaryLibrary.location?.state
                ].filter(Boolean).join(', ')}
              </div>
            </div>
            <div>
              {importStatus[primaryLibrary.id] === 'pending' && (
                <span className="text-gray-500">Pending</span>
              )}
              {importStatus[primaryLibrary.id] === 'importing' && (
                <div className="flex items-center text-blue-500">
                  <Loader className="h-5 w-5 mr-1 animate-spin" />
                  <span>Importing...</span>
                </div>
              )}
              {importStatus[primaryLibrary.id] === 'success' && (
                <div className="flex items-center text-green-500">
                  <CheckCircle className="h-5 w-5 mr-1" />
                  <span>Imported</span>
                </div>
              )}
              {importStatus[primaryLibrary.id] === 'error' && (
                <div className="flex items-center text-red-500">
                  <XCircle className="h-5 w-5 mr-1" />
                  <span>Failed</span>
                </div>
              )}
            </div>
          </li>
          
          {comparisonLibraries.map((library) => (
            <li key={library.id} className="flex items-center justify-between border rounded-md p-3">
              <div>
                <div className="font-medium">{library.name}</div>
                <div className="text-sm text-gray-500">
                  {[
                    library.location?.city,
                    library.location?.state
                  ].filter(Boolean).join(', ')}
                </div>
              </div>
              <div>
                {importStatus[library.id] === 'pending' && (
                  <span className="text-gray-500">Pending</span>
                )}
                {importStatus[library.id] === 'importing' && (
                  <div className="flex items-center text-blue-500">
                    <Loader className="h-5 w-5 mr-1 animate-spin" />
                    <span>Importing...</span>
                  </div>
                )}
                {importStatus[library.id] === 'success' && (
                  <div className="flex items-center text-green-500">
                    <CheckCircle className="h-5 w-5 mr-1" />
                    <span>Imported</span>
                  </div>
                )}
                {importStatus[library.id] === 'error' && (
                  <div className="flex items-center text-red-500">
                    <XCircle className="h-5 w-5 mr-1" />
                    <span>Failed</span>
                  </div>
                )}
              </div>
            </li>
          ))}
        </ul>
      </div>
      
      <div className="flex justify-between">
        <Button 
          onClick={onBack} 
          variant="outline" 
          className="px-6 py-2"
          disabled={isImporting}
        >
          Back
        </Button>
        
        {!isImporting && !isImportComplete() && (
          <Button 
            onClick={startImport} 
            className="px-6 py-2"
          >
            Start Import
          </Button>
        )}
        
        {isImportComplete() && (
          <Button 
            onClick={onComplete} 
            className="px-6 py-2"
            disabled={!isImportSuccessful()}
          >
            {isImportSuccessful() ? 'Continue' : 'Retry Import'}
          </Button>
        )}
      </div>
    </div>
  );
};

export default DataImportStep; 