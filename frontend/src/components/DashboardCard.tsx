import React from 'react';

interface DashboardCardProps {
  title: string;
  children: React.ReactNode;
  className?: string;
  actions?: React.ReactNode;
  icon?: React.ReactNode;
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'danger' | 'info';
}

/**
 * Modern card component for dashboard metrics and charts
 * Supports different color variants and dark mode
 */
const DashboardCard = ({ 
  title, 
  children, 
  className = '', 
  actions,
  icon,
  variant = 'default'
}: DashboardCardProps) => {
  // Color variations based on variant prop
  const variantStyles = {
    default: 'border-gray-200 dark:border-gray-700',
    primary: 'border-blue-200 dark:border-blue-800',
    success: 'border-green-200 dark:border-green-800',
    warning: 'border-yellow-200 dark:border-yellow-800',
    danger: 'border-red-200 dark:border-red-800',
    info: 'border-indigo-200 dark:border-indigo-800'
  };

  return (
    <div 
      className={`
        bg-white dark:bg-gray-800 
        border ${variantStyles[variant]} 
        rounded-xl shadow-sm hover:shadow-md 
        transition-all duration-200 ease-in-out 
        overflow-hidden 
        ${className}
      `}
    >
      <div className="flex justify-between items-center p-4 border-b border-gray-100 dark:border-gray-700">
        <div className="flex items-center space-x-2">
          {icon && <span className="text-gray-500 dark:text-gray-400">{icon}</span>}
          <h2 className="text-lg font-semibold text-gray-800 dark:text-white">{title}</h2>
        </div>
        {actions && (
          <div className="flex space-x-2">
            {actions}
          </div>
        )}
      </div>
      <div className="p-4">
        {children}
      </div>
    </div>
  );
};

export default DashboardCard; 