import React, { forwardRef } from 'react';

interface CheckboxProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: string;
  helperText?: string;
  error?: string;
}

export const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(
  ({ 
    label, 
    helperText, 
    error, 
    className = '', 
    id,
    ...props 
  }, ref) => {
    // Generate a random ID if one isn't provided
    const checkboxId = id || `checkbox-${Math.random().toString(36).substring(2, 9)}`;
    
    return (
      <div className={`flex items-start ${className}`}>
        <div className="flex items-center h-5">
          <input
            ref={ref}
            id={checkboxId}
            type="checkbox"
            className={`
              h-4 w-4 rounded border-gray-300 text-blue-600 
              focus:ring-blue-500
              ${error ? 'border-red-300' : 'border-gray-300'}
              ${props.disabled ? 'bg-gray-100' : ''}
            `}
            {...props}
          />
        </div>
        
        <div className="ml-3 text-sm">
          {label && (
            <label 
              htmlFor={checkboxId} 
              className={`font-medium ${props.disabled ? 'text-gray-500' : 'text-gray-700'}`}
            >
              {label}
            </label>
          )}
          
          {(helperText || error) && (
            <p className={`mt-1 ${error ? 'text-red-600' : 'text-gray-500'}`}>
              {error || helperText}
            </p>
          )}
        </div>
      </div>
    );
  }
); 