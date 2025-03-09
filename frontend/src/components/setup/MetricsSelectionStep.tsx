import React, { useState, useEffect } from 'react';
import { ChevronRight, ChevronLeft, Loader } from 'lucide-react';

import { LibraryConfigCreate, MetricsConfig } from '../../services/libraryConfigService';

interface MetricsSelectionStepProps {
  formData: Partial<LibraryConfigCreate>;
  updateFormData: (data: Partial<LibraryConfigCreate>) => void;
  metricsData?: MetricsConfig;
  isLoading: boolean;
  onNext: () => void;
  onBack: () => void;
}

const MetricsSelectionStep: React.FC<MetricsSelectionStepProps> = ({
  formData,
  updateFormData,
  metricsData,
  isLoading,
  onNext,
  onBack
}) => {
  const [selectedCategories, setSelectedCategories] = useState({
    collection: formData.collection_stats_enabled ?? true,
    usage: formData.usage_stats_enabled ?? true,
    program: formData.program_stats_enabled ?? true,
    staff: formData.staff_stats_enabled ?? true,
    financial: formData.financial_stats_enabled ?? true
  });
  
  const [selectedMetrics, setSelectedMetrics] = useState({
    collection: formData.collection_metrics ?? {},
    usage: formData.usage_metrics ?? {},
    program: formData.program_metrics ?? {},
    staff: formData.staff_metrics ?? {},
    financial: formData.financial_metrics ?? {}
  });
  
  // Initialize metrics checkboxes when data is loaded
  useEffect(() => {
    if (metricsData && !isLoading) {
      // For each category, if we don't have any metrics selected yet,
      // pre-select all available metrics
      const newSelectedMetrics = { ...selectedMetrics };
      
      Object.entries(metricsData.categories).forEach(([category, metrics]) => {
        if (
          Object.keys(selectedMetrics[category as keyof typeof selectedMetrics] || {}).length === 0 &&
          selectedCategories[category as keyof typeof selectedCategories]
        ) {
          const allSelected = Object.keys(metrics).reduce((acc, metricKey) => {
            acc[metricKey] = true;
            return acc;
          }, {} as Record<string, boolean>);
          
          newSelectedMetrics[category as keyof typeof selectedMetrics] = allSelected;
        }
      });
      
      setSelectedMetrics(newSelectedMetrics);
    }
  }, [metricsData, isLoading]);
  
  const handleCategoryToggle = (category: string) => {
    const newSelectedCategories = {
      ...selectedCategories,
      [category]: !selectedCategories[category as keyof typeof selectedCategories]
    };
    
    setSelectedCategories(newSelectedCategories);
    
    // Update form data
    updateFormData({
      collection_stats_enabled: newSelectedCategories.collection,
      usage_stats_enabled: newSelectedCategories.usage,
      program_stats_enabled: newSelectedCategories.program,
      staff_stats_enabled: newSelectedCategories.staff,
      financial_stats_enabled: newSelectedCategories.financial
    });
  };
  
  const handleMetricToggle = (category: string, metricKey: string) => {
    const currentMetrics = selectedMetrics[category as keyof typeof selectedMetrics] || {};
    const newMetrics = {
      ...currentMetrics,
      [metricKey]: !currentMetrics[metricKey]
    };
    
    const newSelectedMetrics = {
      ...selectedMetrics,
      [category]: newMetrics
    };
    
    setSelectedMetrics(newSelectedMetrics);
    
    // Update form data
    updateFormData({
      [`${category}_metrics`]: newMetrics
    } as Partial<LibraryConfigCreate>);
  };
  
  const handleSelectAll = (category: string) => {
    if (!metricsData) return;
    
    const metrics = metricsData.categories[category as keyof typeof metricsData.categories];
    const allSelected = Object.keys(metrics).reduce((acc, metricKey) => {
      acc[metricKey] = true;
      return acc;
    }, {} as Record<string, boolean>);
    
    const newSelectedMetrics = {
      ...selectedMetrics,
      [category]: allSelected
    };
    
    setSelectedMetrics(newSelectedMetrics);
    
    // Update form data
    updateFormData({
      [`${category}_metrics`]: allSelected
    } as Partial<LibraryConfigCreate>);
  };
  
  const handleDeselectAll = (category: string) => {
    if (!metricsData) return;
    
    const metrics = metricsData.categories[category as keyof typeof metricsData.categories];
    const allDeselected = Object.keys(metrics).reduce((acc, metricKey) => {
      acc[metricKey] = false;
      return acc;
    }, {} as Record<string, boolean>);
    
    const newSelectedMetrics = {
      ...selectedMetrics,
      [category]: allDeselected
    };
    
    setSelectedMetrics(newSelectedMetrics);
    
    // Update form data
    updateFormData({
      [`${category}_metrics`]: allDeselected
    } as Partial<LibraryConfigCreate>);
  };
  
  const handleContinue = () => {
    // Make sure at least one category is selected
    if (
      !selectedCategories.collection &&
      !selectedCategories.usage &&
      !selectedCategories.program &&
      !selectedCategories.staff &&
      !selectedCategories.financial
    ) {
      alert('Please select at least one statistics category to continue.');
      return;
    }
    
    onNext();
  };
  
  if (isLoading || !metricsData) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <Loader className="w-8 h-8 text-blue-500 animate-spin mb-4" />
        <p>Loading available metrics...</p>
      </div>
    );
  }
  
  return (
    <div>
      <h2 className="text-2xl font-semibold mb-4">Select Statistics Categories</h2>
      <p className="text-gray-600 mb-6">
        Choose which categories of statistics you want to track for your library.
        You can select specific metrics within each category.
      </p>
      
      <div className="space-y-6">
        {metricsData && Object.entries(metricsData.categories).map(([category, metrics]) => (
          <div key={category} className="border rounded-lg p-4">
            <div className="flex items-center mb-4">
              <input
                type="checkbox"
                id={`category-${category}`}
                className="w-5 h-5 text-blue-600 rounded"
                checked={selectedCategories[category as keyof typeof selectedCategories] || false}
                onChange={() => handleCategoryToggle(category)}
              />
              <label htmlFor={`category-${category}`} className="ml-2 text-lg font-medium capitalize">
                {category} Statistics
              </label>
            </div>
            
            {selectedCategories[category as keyof typeof selectedCategories] && (
              <div className="ml-6">
                <div className="flex items-center justify-end space-x-4 mb-3">
                  <button
                    className="text-sm text-blue-600 hover:text-blue-800"
                    onClick={() => handleSelectAll(category)}
                  >
                    Select All
                  </button>
                  <button
                    className="text-sm text-blue-600 hover:text-blue-800"
                    onClick={() => handleDeselectAll(category)}
                  >
                    Deselect All
                  </button>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {Object.entries(metrics).map(([metricKey, metricName]) => (
                    <div key={metricKey} className="flex items-center">
                      <input
                        type="checkbox"
                        id={`metric-${category}-${metricKey}`}
                        className="w-4 h-4 text-blue-600 rounded"
                        checked={
                          selectedMetrics[category as keyof typeof selectedMetrics]?.[metricKey] || false
                        }
                        onChange={() => handleMetricToggle(category, metricKey)}
                      />
                      <label
                        htmlFor={`metric-${category}-${metricKey}`}
                        className="ml-2 text-sm"
                      >
                        {metricName}
                      </label>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
      
      <div className="mt-8 flex justify-between">
        <button
          className="px-6 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
          onClick={onBack}
        >
          <ChevronLeft className="w-5 h-5 inline -ml-1 mr-1" />
          Back
        </button>
        
        <button
          className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          onClick={handleContinue}
        >
          Continue
          <ChevronRight className="w-5 h-5 inline -mr-1 ml-1" />
        </button>
      </div>
    </div>
  );
};

export default MetricsSelectionStep; 