import { ExclamationTriangleIcon, ArrowPathIcon } from '@heroicons/react/24/outline';

interface ErrorMessageProps {
  message: string;
  onRetry?: () => void;
  variant?: 'danger' | 'warning' | 'info';
}

/**
 * Error message component with different severity levels and dark mode support
 * @param message - The error message to display
 * @param onRetry - Optional callback function for retry button
 * @param variant - Visual style variant (danger, warning, info)
 */
const ErrorMessage = ({ 
  message, 
  onRetry, 
  variant = 'danger' 
}: ErrorMessageProps) => {
  // Style variations based on severity
  const styles = {
    danger: {
      bg: 'bg-red-50 dark:bg-red-900/40',
      border: 'border-red-500 dark:border-red-600',
      text: 'text-red-700 dark:text-red-200',
      icon: 'text-red-500 dark:text-red-400',
      button: 'bg-red-600 hover:bg-red-700 dark:bg-red-700 dark:hover:bg-red-800'
    },
    warning: {
      bg: 'bg-yellow-50 dark:bg-yellow-900/40',
      border: 'border-yellow-500 dark:border-yellow-600',
      text: 'text-yellow-700 dark:text-yellow-200',
      icon: 'text-yellow-500 dark:text-yellow-400',
      button: 'bg-yellow-600 hover:bg-yellow-700 dark:bg-yellow-700 dark:hover:bg-yellow-800'
    },
    info: {
      bg: 'bg-blue-50 dark:bg-blue-900/40',
      border: 'border-blue-500 dark:border-blue-600',
      text: 'text-blue-700 dark:text-blue-200',
      icon: 'text-blue-500 dark:text-blue-400',
      button: 'bg-blue-600 hover:bg-blue-700 dark:bg-blue-700 dark:hover:bg-blue-800'
    }
  };

  const style = styles[variant];

  return (
    <div className={`${style.bg} border-l-4 ${style.border} p-5 rounded-md shadow-sm transition-colors duration-200 my-4`}>
      <div className="flex items-start">
        <div className="flex-shrink-0">
          <ExclamationTriangleIcon className={`h-6 w-6 ${style.icon}`} aria-hidden="true" />
        </div>
        <div className="ml-3">
          <p className={`text-sm font-medium ${style.text}`}>
            {message}
          </p>
          {onRetry && (
            <button 
              onClick={onRetry}
              className={`mt-3 px-4 py-2 text-sm font-medium rounded-md text-white ${style.button} focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-${variant === 'danger' ? 'red' : variant === 'warning' ? 'yellow' : 'blue'}-500 transition-colors duration-200 flex items-center`}
            >
              <ArrowPathIcon className="mr-1.5 h-4 w-4" />
              Try Again
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default ErrorMessage; 