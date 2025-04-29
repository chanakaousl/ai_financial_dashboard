import { useTheme } from '../contexts/ThemeContext';
import { SunIcon, MoonIcon } from '@heroicons/react/24/outline';

/**
 * ThemeToggle component for switching between light and dark mode
 * Uses a smooth transition animation for better UX
 */
const ThemeToggle = () => {
  const { theme, toggleTheme } = useTheme();
  
  return (
    <button
      onClick={toggleTheme}
      className="relative inline-flex items-center justify-center p-2 rounded-full 
                transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 
                focus:ring-offset-2 focus:ring-blue-500
                dark:bg-gray-800 dark:text-gray-100 bg-white text-gray-800 
                hover:bg-gray-100 dark:hover:bg-gray-700"
      aria-label={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
      title={`Switch to ${theme === 'light' ? 'dark' : 'light'} mode`}
    >
      {theme === 'light' ? (
        <MoonIcon className="h-5 w-5 text-gray-700" />
      ) : (
        <SunIcon className="h-5 w-5 text-yellow-300" />
      )}
    </button>
  );
};

export default ThemeToggle;
