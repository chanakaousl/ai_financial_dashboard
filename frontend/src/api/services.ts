import apiClient from './client';

// Types for the API responses
export interface ApiResponse<T> {
  status: string;
  data: T;
}

export interface FinancialReport {
  id: number;
  year: number;
  title: string;
  file_path: string;
  metrics?: MetricDataPoint[];
}

export interface FinancialMetric {
  id: number;
  name: string;
  description: string;
  unit: string;
  category: string;
  yearly_data?: YearlyDataPoint[];
}

export interface YearlyDataPoint {
  id: number;
  year: number;
  value: number;
  notes?: string;
}

export interface MetricDataPoint {
  id: number;
  metric_name: string;
  value: number;
  notes?: string;
}

export interface TrendAnalysis {
  metric: {
    id: number;
    name: string;
    unit: string;
    category: string;
  };
  yearly_data: YearlyDataPoint[];
  analysis: {
    trend_line?: {
      slope: number;
      intercept: number;
      r_squared: number;
      p_value: number;
      std_err: number;
    };
    growth?: {
      cagr: number;
      total_change: number;
    };
    yoy_changes: {
      year: number;
      change: number;
    }[];
    anomalies: {
      year: number;
      value: number;
      yoy_change: number;
      deviation: number;
      message: string;
    }[];
  };
}

export interface ShareholderData {
  year: number;
  raw_value: string;
  parsed_data?: string[];
  parse_error?: string;
  notes?: string;
}

// API Services
export const apiServices = {
  // Reports
  getAllReports: async () => {
    const response = await apiClient.get<ApiResponse<FinancialReport[]>>('/reports');
    return response.data;
  },

  getReportById: async (reportId: number) => {
    const response = await apiClient.get<ApiResponse<FinancialReport>>(`/reports/${reportId}`);
    return response.data;
  },

  // Metrics
  getAllMetrics: async () => {
    const response = await apiClient.get<ApiResponse<FinancialMetric[]>>('/metrics');
    return response.data;
  },

  getMetricById: async (metricId: number) => {
    const response = await apiClient.get<ApiResponse<FinancialMetric>>(`/metrics/${metricId}`);
    return response.data;
  },

  getMetricCategories: async () => {
    const response = await apiClient.get<ApiResponse<string[]>>('/metrics/categories');
    return response.data;
  },

  // Analysis
  getMetricTrend: async (metricId: number) => {
    const response = await apiClient.get<ApiResponse<TrendAnalysis>>(`/analysis/trend/${metricId}`);
    return response.data;
  },

  compareMetrics: async (metricIds: number[]) => {
    const queryString = metricIds.map(id => `metric_ids=${id}`).join('&');
    const response = await apiClient.get<ApiResponse<any>>(`/analysis/compare?${queryString}`);
    return response.data;
  },

  // Shareholders
  getShareholdersData: async () => {
    const response = await apiClient.get<ApiResponse<{metric_name: string, metric_id: number, yearly_data: ShareholderData[]}>>('/shareholders');
    return response.data;
  },

  // Utility endpoints
  exportMetricCsv: (metricId: number) => {
    window.open(`${apiClient.defaults.baseURL}/export/metric/${metricId}/csv`, '_blank');
  },

  exportCompareCsv: (metricIds: number[]) => {
    const queryString = metricIds.map(id => `metric_ids=${id}`).join('&');
    window.open(`${apiClient.defaults.baseURL}/export/compare/csv?${queryString}`, '_blank');
  },

  // Health check
  checkApiHealth: async () => {
    const response = await apiClient.get<ApiResponse<{message: string}>>('/health');
    return response.data;
  }
};

export default apiServices; 