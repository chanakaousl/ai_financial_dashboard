import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Dashboard from './views/Dashboard';
import MetricDetail from './views/MetricDetail';
import CompareMetrics from './views/CompareMetrics';
import Shareholders from './views/Shareholders';
import LoadingSpinner from './components/LoadingSpinner';
import ErrorMessage from './components/ErrorMessage';
import apiServices from './api/services';
import { ThemeProvider } from './contexts/ThemeContext';
import './App.css';

/**
 * Main App component that handles routing and API connection state
 */
function App() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [apiConnected, setApiConnected] = useState(false);

  useEffect(() => {
    // Check if API is accessible
    const checkApiConnection = async () => {
      try {
        const response = await apiServices.checkApiHealth();
        if (response.status === 'success') {
          setApiConnected(true);
        } else {
          setError('API connection error: The server is not responding correctly.');
        }
      } catch (err) {
        setError('API connection error: Could not connect to the backend server. Please ensure the backend is running.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    checkApiConnection();
  }, []);

  if (loading) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
        <div className="text-center">
          <LoadingSpinner />
          <p className="mt-4 text-gray-600 dark:text-gray-300">Connecting to the API server...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 p-4 transition-colors duration-200">
        <div className="max-w-md w-full">
          <ErrorMessage 
            message={error} 
            onRetry={() => window.location.reload()}
          />
          <div className="mt-4 bg-yellow-50 dark:bg-yellow-900 border-l-4 border-yellow-400 p-4 rounded transition-colors duration-200">
            <p className="text-sm text-yellow-700 dark:text-yellow-200">
              Make sure the backend server is running at http://localhost:5000.
              <br/>
              Run <code className="bg-gray-100 dark:bg-gray-800 px-1 rounded">cd backend && python run.py</code> to start the server.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <ThemeProvider>
      <Router>
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 transition-colors duration-200">
          <Navbar />
          <div className="container mx-auto px-4 py-6">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/metrics/:id" element={<MetricDetail />} />
              <Route path="/compare" element={<CompareMetrics />} />
              <Route path="/shareholders" element={<Shareholders />} />
            </Routes>
          </div>
        </div>
      </Router>
    </ThemeProvider>
  );
}

export default App;
