import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '@/components/ui/Card';

// Step components
import WelcomeStep from './setup/steps/WelcomeStep';
import LibrarySelectionStep from './setup/steps/LibrarySelectionStep';
import ComparisonLibrariesStep from './setup/steps/ComparisonLibrariesStep';
import DataImportStep from './setup/steps/DataImportStep';
import SetupCompleteStep from './setup/steps/SetupCompleteStep';

const SetupWizard: React.FC = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [selectedLibrary, setSelectedLibrary] = useState<any>(null);
  const [comparisonLibraries, setComparisonLibraries] = useState<any[]>([]);
  
  const handleComplete = () => {
    // Save user preferences and redirect to dashboard
    navigate('/');
  };
  
  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        {/* Progress indicator */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="flex flex-col items-center">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                  i < step ? 'bg-blue-600 text-white' : 
                  i === step ? 'bg-blue-100 border-2 border-blue-600 text-blue-600' : 
                  'bg-gray-200 text-gray-500'
                }`}>
                  {i}
                </div>
                <div className="text-xs mt-2 text-gray-500">
                  {i === 1 && 'Welcome'}
                  {i === 2 && 'Select Library'}
                  {i === 3 && 'Comparisons'}
                  {i === 4 && 'Import Data'}
                  {i === 5 && 'Complete'}
                </div>
              </div>
            ))}
          </div>
        </div>
        
        <Card className="p-6">
          {step === 1 && <WelcomeStep onContinue={() => setStep(2)} />}
          {step === 2 && (
            <LibrarySelectionStep 
              onSelect={setSelectedLibrary} 
              onContinue={() => setStep(3)} 
              selectedLibrary={selectedLibrary}
            />
          )}
          {step === 3 && (
            <ComparisonLibrariesStep 
              primaryLibrary={selectedLibrary}
              selectedLibraries={comparisonLibraries}
              onSelect={setComparisonLibraries}
              onContinue={() => setStep(4)}
              onBack={() => setStep(2)}
            />
          )}
          {step === 4 && (
            <DataImportStep 
              primaryLibrary={selectedLibrary}
              comparisonLibraries={comparisonLibraries}
              onComplete={() => setStep(5)}
              onBack={() => setStep(3)}
            />
          )}
          {step === 5 && (
            <SetupCompleteStep 
              onFinish={handleComplete}
            />
          )}
        </Card>
      </div>
    </div>
  );
};

export default SetupWizard; 