import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ChevronRight, ChevronLeft, CheckCircle } from 'lucide-react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

import { libraryConfigService, LibraryConfigCreate } from '../../services/libraryConfigService';
import LibrarySelectionStep from './LibrarySelectionStep';
import MetricsSelectionStep from './MetricsSelectionStep';
import SummaryStep from './SummaryStep';

// Define the steps of the wizard
const STEPS = [
  { id: 'library', title: 'Select Your Library' },
  { id: 'metrics', title: 'Select Statistics' },
  { id: 'summary', title: 'Review & Finish' }
];

const setupSchema = z.object({
  libraryName: z.string().min(1, 'Library name is required'),
  state: z.string().min(1, 'State is required'),
  year: z.string().regex(/^\d{4}$/, 'Year must be a 4-digit number'),
});

type SetupFormData = z.infer<typeof setupSchema>;

const SetupWizard: React.FC = () => {
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [formData, setFormData] = useState<Partial<LibraryConfigCreate>>({
    collection_stats_enabled: true,
    usage_stats_enabled: true,
    program_stats_enabled: true,
    staff_stats_enabled: true,
    financial_stats_enabled: true,
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
  const { mutate: createConfig, isPending: isSubmitting } = useMutation({
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
    
    // Mark setup as complete and submit
    const configData: LibraryConfigCreate = {
      ...formData as LibraryConfigCreate,
      setup_complete: true
    };
    
    createConfig(configData);
  };
  
  const { register, handleSubmit: formHandleSubmit, formState: { errors } } = useForm<SetupFormData>({
    resolver: zodResolver(setupSchema),
  });

  const onSubmit = async (data: SetupFormData) => {
    try {
      // TODO: Implement setup submission
      console.log('Setup data:', data);
    } catch (error) {
      console.error('Setup failed:', error);
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

      <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
        <h2 className="text-2xl font-bold mb-6">Library Setup</h2>
        <form onSubmit={formHandleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label htmlFor="libraryName" className="block text-sm font-medium text-gray-700">
              Library Name
            </label>
            <input
              {...register('libraryName')}
              type="text"
              id="libraryName"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
            {errors.libraryName && (
              <p className="mt-1 text-sm text-red-600">{errors.libraryName.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="state" className="block text-sm font-medium text-gray-700">
              State
            </label>
            <input
              {...register('state')}
              type="text"
              id="state"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
            {errors.state && (
              <p className="mt-1 text-sm text-red-600">{errors.state.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="year" className="block text-sm font-medium text-gray-700">
              Year
            </label>
            <input
              {...register('year')}
              type="text"
              id="year"
              placeholder="YYYY"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
            {errors.year && (
              <p className="mt-1 text-sm text-red-600">{errors.year.message}</p>
            )}
          </div>

          <button
            type="submit"
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Complete Setup
          </button>
        </form>
      </div>
    </div>
  );
};

export default SetupWizard; 