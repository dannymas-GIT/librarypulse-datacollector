import React from 'react';

interface CardProps {
  title?: string;
  children: React.ReactNode;
  className?: string;
  icon?: React.ReactNode;
}

const Card: React.FC<CardProps> = ({ title, children, className = '', icon }) => {
  return (
    <div className={`bg-white rounded-lg shadow p-6 ${className}`}>
      {(title || icon) && (
        <div className="flex items-center mb-4">
          {icon && <div className="mr-3">{icon}</div>}
          {title && <h2 className="text-xl font-semibold text-gray-800">{title}</h2>}
        </div>
      )}
      <div>{children}</div>
    </div>
  );
};

export default Card; 