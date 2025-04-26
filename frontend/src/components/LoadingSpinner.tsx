import { useTheme } from '../hooks/useTheme';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  showText?: boolean;
  text?: string;
}

/**
 * Modern loading spinner with size options and theme support
 */
const LoadingSpinner = ({ 
  size = 'md', 
  showText = true, 
  text = 'Loading...' 
}: LoadingSpinnerProps) => {
  const { theme } = useTheme();
  
  // Size variations
  const sizeClasses = {
    sm: 'h-6 w-6 border-2',
    md: 'h-10 w-10 border-2',
    lg: 'h-16 w-16 border-3'
  };
  
  return (
    <div className="flex flex-col justify-center items-center py-4">
      <div className={`
        animate-spin 
        rounded-full 
        ${sizeClasses[size]} 
        border-transparent 
        border-t-blue-600 dark:border-t-blue-400
        border-r-blue-600 dark:border-r-blue-400
        ${theme === 'dark' ? 'opacity-80' : 'opacity-100'}
        transition-opacity duration-300
      `}></div>
      
      {showText && (
        <span className="mt-3 text-gray-600 dark:text-gray-300 text-sm font-medium">
          {text}
        </span>
      )}
    </div>
  );
};

export default LoadingSpinner; 