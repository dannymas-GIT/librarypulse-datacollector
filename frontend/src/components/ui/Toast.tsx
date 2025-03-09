import React, { useState, useEffect } from 'react';
import { X, Check, AlertCircle, Info } from 'lucide-react';

export type ToastType = 'success' | 'error' | 'info' | 'warning';

interface ToastProps {
  type: ToastType;
  message: string;
  duration?: number;
  onClose: () => void;
  isVisible: boolean;
}

export const Toast: React.FC<ToastProps> = ({
  type,
  message,
  duration = 5000,
  onClose,
  isVisible,
}) => {
  const [isClosing, setIsClosing] = useState(false);

  useEffect(() => {
    if (!isVisible) return;

    const timer = setTimeout(() => {
      setIsClosing(true);
      setTimeout(onClose, 300); // Wait for animation to complete
    }, duration);

    return () => {
      clearTimeout(timer);
    };
  }, [isVisible, duration, onClose]);

  const handleClose = () => {
    setIsClosing(true);
    setTimeout(onClose, 300); // Wait for animation to complete
  };

  if (!isVisible) return null;

  const typeConfig = {
    success: {
      icon: <Check className="w-5 h-5" />,
      bgColor: 'bg-green-50',
      textColor: 'text-green-800',
      borderColor: 'border-green-400',
      iconColor: 'text-green-500',
    },
    error: {
      icon: <AlertCircle className="w-5 h-5" />,
      bgColor: 'bg-red-50',
      textColor: 'text-red-800',
      borderColor: 'border-red-400',
      iconColor: 'text-red-500',
    },
    warning: {
      icon: <AlertCircle className="w-5 h-5" />,
      bgColor: 'bg-yellow-50',
      textColor: 'text-yellow-800',
      borderColor: 'border-yellow-400',
      iconColor: 'text-yellow-500',
    },
    info: {
      icon: <Info className="w-5 h-5" />,
      bgColor: 'bg-blue-50',
      textColor: 'text-blue-800',
      borderColor: 'border-blue-400',
      iconColor: 'text-blue-500',
    },
  };

  const config = typeConfig[type];

  return (
    <div
      className={`
        fixed bottom-4 right-4 z-50 flex items-start p-4 mb-4 w-full max-w-xs
        rounded-lg shadow-lg border-l-4 ${config.bgColor} ${config.borderColor}
        transform transition-all duration-300 ease-in-out
        ${isClosing ? 'translate-x-full opacity-0' : 'translate-x-0 opacity-100'}
      `}
      role="alert"
    >
      <div className={`inline-flex flex-shrink-0 mr-3 ${config.iconColor}`}>
        {config.icon}
      </div>
      <div className={`ml-3 ${config.textColor} mr-8 text-sm font-medium`}>
        {message}
      </div>
      <button
        type="button"
        className={`
          ml-auto -mx-1.5 -my-1.5 ${config.bgColor} ${config.textColor} 
          rounded-lg p-1.5 inline-flex h-8 w-8 focus:outline-none
        `}
        onClick={handleClose}
        aria-label="Close"
      >
        <X className="w-5 h-5" />
      </button>
    </div>
  );
}; 