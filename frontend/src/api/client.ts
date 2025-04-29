import axios from 'axios';

// Create an axios instance with base URL
const apiClient = axios.create({
  baseURL: 'http://localhost:5000/api', // Use the full URL to the backend API
  headers: {
    'Content-Type': 'application/json',
  },
});

export default apiClient;