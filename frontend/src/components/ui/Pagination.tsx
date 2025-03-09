import React from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';

interface PaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  className?: string;
}

export const Pagination: React.FC<PaginationProps> = ({
  currentPage,
  totalPages,
  onPageChange,
  className = ''
}) => {
  const handlePrevious = () => {
    if (currentPage > 1) {
      onPageChange(currentPage - 1);
    }
  };

  const handleNext = () => {
    if (currentPage < totalPages) {
      onPageChange(currentPage + 1);
    }
  };

  // Generate page numbers to display
  const getPageNumbers = () => {
    const pages = [];
    const maxPagesToShow = 5;
    
    if (totalPages <= maxPagesToShow) {
      // Show all pages if there are fewer than maxPagesToShow
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      // Always show first page
      pages.push(1);
      
      // Calculate start and end of page range
      let start = Math.max(2, currentPage - 1);
      let end = Math.min(totalPages - 1, currentPage + 1);
      
      // Adjust if we're at the beginning or end
      if (currentPage <= 2) {
        end = 3;
      } else if (currentPage >= totalPages - 1) {
        start = totalPages - 2;
      }
      
      // Add ellipsis if needed
      if (start > 2) {
        pages.push('...');
      }
      
      // Add middle pages
      for (let i = start; i <= end; i++) {
        pages.push(i);
      }
      
      // Add ellipsis if needed
      if (end < totalPages - 1) {
        pages.push('...');
      }
      
      // Always show last page
      pages.push(totalPages);
    }
    
    return pages;
  };

  if (totalPages <= 1) return null;

  return (
    <nav className={`flex items-center justify-center mt-8 ${className}`}>
      <ul className="flex items-center -space-x-px">
        <li>
          <button
            onClick={handlePrevious}
            disabled={currentPage === 1}
            className={`
              flex items-center justify-center h-10 px-4 
              rounded-l-md border border-gray-300
              ${currentPage === 1 
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
                : 'bg-white text-gray-500 hover:bg-gray-50'}
            `}
            aria-label="Previous page"
          >
            <ChevronLeft className="w-5 h-5" />
          </button>
        </li>
        
        {getPageNumbers().map((page, index) => (
          <li key={`page-${index}`}>
            {page === '...' ? (
              <span className="flex items-center justify-center h-10 px-4 border border-gray-300 bg-white text-gray-500">
                ...
              </span>
            ) : (
              <button
                onClick={() => typeof page === 'number' && onPageChange(page)}
                className={`
                  flex items-center justify-center h-10 px-4 
                  border border-gray-300
                  ${currentPage === page 
                    ? 'bg-blue-50 text-blue-600 border-blue-500 z-10' 
                    : 'bg-white text-gray-500 hover:bg-gray-50'}
                `}
                aria-current={currentPage === page ? 'page' : undefined}
              >
                {page}
              </button>
            )}
          </li>
        ))}
        
        <li>
          <button
            onClick={handleNext}
            disabled={currentPage === totalPages}
            className={`
              flex items-center justify-center h-10 px-4 
              rounded-r-md border border-gray-300
              ${currentPage === totalPages 
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed' 
                : 'bg-white text-gray-500 hover:bg-gray-50'}
            `}
            aria-label="Next page"
          >
            <ChevronRight className="w-5 h-5" />
          </button>
        </li>
      </ul>
    </nav>
  );
}; 