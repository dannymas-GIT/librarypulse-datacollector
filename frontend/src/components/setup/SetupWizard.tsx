import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { CheckCircle } from 'lucide-react';

import { libraryConfigService, LibraryConfigCreate } from '../../services/libraryConfigService';
import LibrarySelectionStep from './LibrarySelectionStep';
import ComparisonLibrariesStep from './ComparisonLibrariesStep';
import MetricsSelectionStep from './MetricsSelectionStep';
import SummaryStep from './SummaryStep';

// Define the steps of the wizard
const STEPS = [
  { id: 'library', title: 'Select Your Library' },
  { id: 'comparisons', title: 'Comparison Libraries' },
  { id: 'metrics', title: 'Select Statistics' },
  { id: 'summary', title: 'Review & Finish' }
];

const SetupWizard: React.FC = () => {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [formData, setFormData] = useState<Partial<LibraryConfigCreate>>({
    collection_stats_enabled: true,
    usage_stats_enabled: true,
    program_stats_enabled: true,
    staff_stats_enabled: true,
    financial_stats_enabled: true,
    comparison_libraries: [],
    setup_complete: false,
    auto_update_enabled: true
  });
  
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  
  // Fetch available metrics
  const { data: metricsData, isLoading: metricsLoading } = useQuery({
    queryKey: ['availableMetrics'],
    queryFn: () => libraryConfigService.getAvailableMetrics()
  });
  
  // Mutation for creating the library configuration
  const { mutate: createConfig, isLoading: isSubmitting } = useMutation({
    mutationFn: libraryConfigService.createConfig,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['setupStatus'] });
      navigate('/dashboard');
    }
  });
  
  const currentStep = STEPS[currentStepIndex];
  
  const goToNextStep = () => {
    if (currentStepIndex < STEPS.length - 1) {
      setCurrentStepIndex(prev => prev + 1);
    }
  };
  
  const goToPreviousStep = () => {
    if (currentStepIndex > 0) {
      setCurrentStepIndex(prev => prev - 1);
    }
  };
  
  const updateFormData = (newData: Partial<LibraryConfigCreate>) => {
    setFormData(prev => ({ ...prev, ...newData }));
  };
  
  const handleSubmit = () => {
    // Make sure we have the required fields
    if (!formData.library_id || !formData.library_name) {
      alert('Please select a library to continue.');
      setCurrentStepIndex(0); // Go back to library selection
      return;
    }
    
    console.log('Submitting library configuration:', formData);
    
    // Mark setup as complete and submit
    const configData: LibraryConfigCreate = {
      ...formData as LibraryConfigCreate,
      setup_complete: true
    };
    
    // Start the data import process for the selected libraries
    try {
      createConfig(configData);
      console.log('Configuration submitted successfully');
      // The mutation will handle navigation if successful
    } catch (error) {
      console.error('Error submitting configuration:', error);
      alert('An error occurred while saving your configuration. Please try again.');
    }
  };
  
  // Render the appropriate step
  const renderStep = () => {
    switch (currentStep.id) {
      case 'library':
        return (
          <LibrarySelectionStep 
            formData={formData} 
            updateFormData={updateFormData} 
            onNext={goToNextStep} 
          />
        );
      case 'comparisons':
        return (
          <ComparisonLibrariesStep
            formData={formData}
            updateFormData={updateFormData}
            onNext={goToNextStep}
            onBack={goToPreviousStep}
          />
        );
      case 'metrics':
        return (
          <MetricsSelectionStep 
            formData={formData} 
            updateFormData={updateFormData} 
            metricsData={metricsData}
            isLoading={metricsLoading}
            onNext={goToNextStep}
            onBack={goToPreviousStep}
          />
        );
      case 'summary':
        return (
          <SummaryStep 
            formData={formData} 
            metricsData={metricsData}
            onSubmit={handleSubmit}
            onBack={goToPreviousStep}
            isSubmitting={isSubmitting}
            updateFormData={updateFormData}
          />
        );
      default:
        return null;
    }
  };
  
  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-8">
        <h2 className="text-2xl font-semibold text-center mb-6">
          Welcome to Library Lens
        </h2>
        <p className="text-center text-gray-600 mb-8">
          Let's set up your library profile to get started. This will allow us to focus on the statistics most relevant to you.
        </p>
        
        {/* Progress indicators */}
        <div className="flex justify-between mb-8">
          {STEPS.map((step, index) => (
            <div key={step.id} className="flex flex-col items-center">
              <div 
                className={`w-10 h-10 rounded-full flex items-center justify-center mb-2 
                  ${index < currentStepIndex 
                    ? 'bg-green-500 text-white' 
                    : index === currentStepIndex 
                      ? 'bg-blue-500 text-white' 
                      : 'bg-gray-200 text-gray-500'}`}
              >
                {index < currentStepIndex ? (
                  <CheckCircle className="w-5 h-5" />
                ) : (
                  <span>{index + 1}</span>
                )}
              </div>
              <span className={`text-sm ${index === currentStepIndex ? 'font-medium' : 'text-gray-500'}`}>
                {step.title}
              </span>
            </div>
          ))}
        </div>
      </div>
      
      {/* Step content */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        {renderStep()}
      </div>
      
      {/* THIS COMMENT IS INTENTIONALLY HERE TO MARK THE END OF THE COMPONENT */}
    </div>
  );
};

export default SetupWizard; 