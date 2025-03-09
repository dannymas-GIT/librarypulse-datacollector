import React from 'react';
import { CheckCircle2, ChevronLeft } from 'lucide-react';

import { LibraryConfigCreate, MetricsConfig } from '../../services/libraryConfigService';

interface SummaryStepProps {
  formData: Partial<LibraryConfigCreate>;
  metricsData?: MetricsConfig;
  onSubmit: () => void;
  onBack: () => void;
  isSubmitting: boolean;
}

const SummaryStep: React.FC<SummaryStepProps> = ({
  formData,
  metricsData,
  onSubmit,
  onBack,
  isSubmitting
}) => {
  const renderCategorySelection = () => {
    return (
      <div className="mb-6">
        <h3 className="text-lg font-medium mb-2">Selected Categories</h3>
        <div className="space-y-2">
          {formData.collection_stats_enabled && (
            <div className="flex items-center">
              <CheckCircle2 className="w-5 h-5 text-green-500 mr-2" />
              <span>Collection Statistics</span>
            </div>
          )}
          {formData.usage_stats_enabled && (
            <div className="flex items-center">
              <CheckCircle2 className="w-5 h-5 text-green-500 mr-2" />
              <span>Usage Statistics</span>
            </div>
          )}
          {formData.program_stats_enabled && (
            <div className="flex items-center">
              <CheckCircle2 className="w-5 h-5 text-green-500 mr-2" />
              <span>Program Statistics</span>
            </div>
          )}
          {formData.staff_stats_enabled && (
            <div className="flex items-center">
              <CheckCircle2 className="w-5 h-5 text-green-500 mr-2" />
              <span>Staff Statistics</span>
            </div>
          )}
          {formData.financial_stats_enabled && (
            <div className="flex items-center">
              <CheckCircle2 className="w-5 h-5 text-green-500 mr-2" />
              <span>Financial Statistics</span>
            </div>
          )}
        </div>
      </div>
    );
  };
  
  const renderMetricsSelection = (category: string, displayName: string) => {
    const enabledKey = `${category}_stats_enabled` as keyof LibraryConfigCreate;
    const metricsKey = `${category}_metrics` as keyof LibraryConfigCreate;
    
    if (!formData[enabledKey]) return null;
    
    const selectedMetrics = formData[metricsKey] as Record<string, boolean> | undefined;
    if (!selectedMetrics || !metricsData) return null;
    
    const categoryMetrics = metricsData.categories[category as keyof typeof metricsData.categories];
    const enabledMetrics = Object.entries(selectedMetrics)
      .filter(([_, enabled]) => enabled)
      .map(([key]) => categoryMetrics[key]);
    
    if (enabledMetrics.length === 0) return null;
    
    return (
      <div className="mb-6">
        <h3 className="text-lg font-medium mb-2">{displayName} Metrics</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {enabledMetrics.map((metricName, index) => (
            <div key={index} className="flex items-center">
              <CheckCircle2 className="w-4 h-4 text-green-500 mr-2" />
              <span className="text-sm">{metricName}</span>
            </div>
          ))}
        </div>
      </div>
    );
  };
  
  return (
    <div>
      <h2 className="text-2xl font-semibold mb-4">Review Your Configuration</h2>
      <p className="text-gray-600 mb-6">
        Please review your library and statistics selections below. Once you finish setup, 
        we'll download the necessary data for your library and prepare your dashboard.
      </p>
      
      {/* Selected Library */}
      <div className="mb-6">
        <h3 className="text-lg font-medium mb-2">Selected Library</h3>
        <div className="border rounded-lg p-4 bg-blue-50">
          <div className="font-medium">{formData.library_name}</div>
          <div className="text-sm text-gray-500">ID: {formData.library_id}</div>
        </div>
      </div>
      
      {/* Selected Categories */}
      {renderCategorySelection()}
      
      {/* Selected Metrics */}
      <div className="border rounded-lg p-4 bg-gray-50 mb-6">
        <h3 className="text-lg font-medium mb-4">Selected Metrics</h3>
        
        {renderMetricsSelection('collection', 'Collection')}
        {renderMetricsSelection('usage', 'Usage')}
        {renderMetricsSelection('program', 'Program')}
        {renderMetricsSelection('staff', 'Staff')}
        {renderMetricsSelection('financial', 'Financial')}
      </div>
      
      {/* Automatic Updates */}
      <div className="mb-6">
        <h3 className="text-lg font-medium mb-2">Data Updates</h3>
        <div className="flex items-center">
          <input
            type="checkbox"
            id="auto-update"
            className="w-5 h-5 text-blue-600 rounded"
            checked={formData.auto_update_enabled ?? true}
            onChange={(e) => onSubmit({ ...formData, auto_update_enabled: e.target.checked })}
          />
          <label htmlFor="auto-update" className="ml-2">
            Automatically check for and download the latest data when available
          </label>
        </div>
      </div>
      
      {/* Action buttons */}
      <div className="mt-8 flex justify-between">
        <button
          className="px-6 py-2 border border-gray-300 rounded-md hover:bg-gray-50"
          onClick={onBack}
          disabled={isSubmitting}
        >
          <ChevronLeft className="w-5 h-5 inline -ml-1 mr-1" />
          Back
        </button>
        
        <button
          className="px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-green-300 disabled:cursor-not-allowed"
          onClick={onSubmit}
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Finalizing Setup...' : 'Complete Setup'}
        </button>
      </div>
    </div>
  );
};

export default SummaryStep; 