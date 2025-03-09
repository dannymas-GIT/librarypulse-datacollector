import React from 'react';
import { ArrowUpDown } from 'lucide-react';

export interface TableColumn<T> {
  header: string;
  accessor: keyof T | ((data: T) => React.ReactNode);
  sortable?: boolean;
  className?: string;
}

interface TableProps<T> {
  data: T[];
  columns: TableColumn<T>[];
  keyExtractor: (item: T) => string | number;
  onRowClick?: (item: T) => void;
  sortColumn?: keyof T;
  sortDirection?: 'asc' | 'desc';
  onSort?: (column: keyof T) => void;
  isLoading?: boolean;
  emptyMessage?: string;
  className?: string;
}

export function Table<T>({
  data,
  columns,
  keyExtractor,
  onRowClick,
  sortColumn,
  sortDirection,
  onSort,
  isLoading = false,
  emptyMessage = 'No data available',
  className = ''
}: TableProps<T>) {
  const renderCell = (item: T, column: TableColumn<T>) => {
    if (typeof column.accessor === 'function') {
      return column.accessor(item);
    }
    
    return item[column.accessor] as React.ReactNode;
  };

  const handleHeaderClick = (column: TableColumn<T>) => {
    if (column.sortable && onSort && typeof column.accessor !== 'function') {
      onSort(column.accessor as keyof T);
    }
  };

  return (
    <div className={`overflow-x-auto ${className}`}>
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            {columns.map((column, index) => (
              <th
                key={`header-${index}`}
                scope="col"
                className={`
                  px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider
                  ${column.sortable ? 'cursor-pointer hover:bg-gray-100' : ''}
                  ${column.className || ''}
                `}
                onClick={() => column.sortable && handleHeaderClick(column)}
              >
                <div className="flex items-center space-x-1">
                  <span>{column.header}</span>
                  {column.sortable && (
                    <ArrowUpDown 
                      className={`
                        w-4 h-4
                        ${typeof column.accessor !== 'function' && sortColumn === column.accessor
                          ? 'text-blue-600'
                          : 'text-gray-400'
                        }
                      `}
                    />
                  )}
                </div>
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {isLoading ? (
            <tr>
              <td 
                colSpan={columns.length} 
                className="px-6 py-4 text-center text-sm text-gray-500"
              >
                Loading...
              </td>
            </tr>
          ) : data.length === 0 ? (
            <tr>
              <td 
                colSpan={columns.length} 
                className="px-6 py-4 text-center text-sm text-gray-500"
              >
                {emptyMessage}
              </td>
            </tr>
          ) : (
            data.map((item) => (
              <tr 
                key={keyExtractor(item)}
                className={onRowClick ? 'cursor-pointer hover:bg-gray-50' : ''}
                onClick={() => onRowClick && onRowClick(item)}
              >
                {columns.map((column, cellIndex) => (
                  <td 
                    key={`cell-${keyExtractor(item)}-${cellIndex}`}
                    className={`px-6 py-4 whitespace-nowrap text-sm text-gray-500 ${column.className || ''}`}
                  >
                    {renderCell(item, column)}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
} 