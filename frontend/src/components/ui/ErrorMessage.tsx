import React from 'react';
import { AlertCircle } from 'lucide-react';
import { ApiError } from '@/utils/api';

interface ErrorMessageProps {
  error: ApiError | Error | string | null;
  className?: string;
}

export const ErrorMessage: React.FC<ErrorMessageProps> = ({ 
  error, 
  className = '' 
}) => {
  if (!error) return null;

  let errorMessage: string;
  let statusCode: number | undefined;

  if (typeof error === 'string') {
    errorMessage = error;
  } else if ('status' in error && 'message' in error) {
    // It's an ApiError
    errorMessage = error.message;
    statusCode = error.status;
  } else if (error instanceof Error) {
    errorMessage = error.message;
  } else {
    errorMessage = 'An unknown error occurred';
  }

  return (
    <div className={`flex items-start gap-2 p-4 text-red-600 bg-red-50 rounded-md ${className}`}>
      <AlertCircle className="w-5 h-5 mt-0.5 flex-shrink-0" />
      <div>
        {statusCode && (
          <span className="font-semibold mr-2">Error {statusCode}:</span>
        )}
        <span>{errorMessage}</span>
      </div>
    </div>
  );
}; 