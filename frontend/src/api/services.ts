import axios from 'axios';

// Create axios instance with base URL
const api = axios.create({
  baseURL: 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Define API response types
interface ApiResponse<T> {
  status: string;
  data: T;
  message?: string;
}

interface Metric {
  id: number;
  name: string;
  display_name: string;
  description: string;
  unit: string;
  category: string;
  visualization_type: string;
}

interface YearlyData {
  year: number;
  value: number;
}

interface MetricWithData extends Metric {
  yearly_data: YearlyData[];
  annotations?: Record<string, any>;
}

interface Report {
  id: number;
  year: number;
  pdf_path: string;
}

interface ReportWithMetrics extends Report {
  metrics: {
    id: number;
    name: string;
    display_name: string;
    value: number;
    unit: string;
  }[];
}

interface ShareholderData {
  id: number;
  year: number;
  rank: number;
  name: string;
  percentage: number;
  shares: number;
}

interface ShareholdersResponse {
  years: {
    [key: string]: ShareholderData[];
  };
}

// API service methods
const apiServices = {
  /**
   * Check API health
   */
  checkApiHealth: async (): Promise<ApiResponse<{ message: string }>> => {
    try {
      const response = await api.get<ApiResponse<{ message: string }>>('/health');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Get all metrics
   */
  getAllMetrics: async (): Promise<ApiResponse<Metric[]>> => {
    try {
      const response = await api.get<ApiResponse<Metric[]>>('/metrics');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Get a specific metric by ID with yearly data
   */
  getMetricById: async (id: number): Promise<ApiResponse<MetricWithData>> => {
    try {
      const response = await api.get<ApiResponse<MetricWithData>>(`/metrics/${id}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Get all financial reports
   */
  getAllReports: async (): Promise<ApiResponse<Report[]>> => {
    try {
      const response = await api.get<ApiResponse<Report[]>>('/reports');
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Get a specific report by ID with metric data
   */
  getReportById: async (id: number): Promise<ApiResponse<ReportWithMetrics>> => {
    try {
      const response = await api.get<ApiResponse<ReportWithMetrics>>(`/reports/${id}`);
      return response.data;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Get shareholders data
   * @param year Optional year filter
   */
  getShareholders: async (year?: number): Promise<ApiResponse<ShareholdersResponse>> => {
    try {
      const url = year ? `/shareholders?year=${year}` : '/shareholders';
      const response = await api.get<ApiResponse<ShareholdersResponse>>(url);
      return response.data;
    } catch (error) {
      throw error;
    }
  }
};

export default apiServices;
export type { 
  Metric, 
  YearlyData, 
  MetricWithData, 
  Report, 
  ReportWithMetrics, 
  ShareholderData, 
  ShareholdersResponse 
}; 