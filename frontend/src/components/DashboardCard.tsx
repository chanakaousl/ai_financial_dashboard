import React from 'react';

interface DashboardCardProps {
  title: string;
  children: React.ReactNode;
  className?: string;
  actions?: React.ReactNode;
}

const DashboardCard = ({ 
  title, 
  children, 
  className = '', 
  actions 
}: DashboardCardProps) => {
  return (
    <div className={`bg-white rounded-lg shadow-md overflow-hidden ${className}`}>
      <div className="flex justify-between items-center border-b p-4">
        <h2 className="text-lg font-semibold">{title}</h2>
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