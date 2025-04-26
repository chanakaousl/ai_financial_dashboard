import axios from 'axios';

// Create an axios instance with base URL
const apiClient = axios.create({
  baseURL: '/api', // Use relative path which will be handled by the Vite proxy
  headers: {
    'Content-Type': 'application/json',
  },
});

export default apiClient; 