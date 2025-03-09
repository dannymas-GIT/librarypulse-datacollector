import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  title?: string;
  subtitle?: string;
  footer?: React.ReactNode;
  headerAction?: React.ReactNode;
}

export const Card: React.FC<CardProps> = ({
  children,
  className = '',
  title,
  subtitle,
  footer,
  headerAction
}) => {
  return (
    <div className={`bg-white rounded-lg shadow-md overflow-hidden ${className}`}>
      {(title || subtitle) && (
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <div>
              {title && <h3 className="text-lg font-semibold text-gray-800">{title}</h3>}
              {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
            </div>
            {headerAction && (
              <div className="ml-4">{headerAction}</div>
            )}
          </div>
        </div>
      )}
      
      <div className="px-6 py-4">
        {children}
      </div>
      
      {footer && (
        <div className="px-6 py-3 bg-gray-50 border-t border-gray-200">
          {footer}
        </div>
      )}
    </div>
  );
}; 