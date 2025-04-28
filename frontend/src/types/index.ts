import { 
  Metric, 
  YearlyData, 
  MetricWithData, 
  Report, 
  ReportWithMetrics,
  ShareholderData,
  ShareholdersResponse 
} from '../api/services';

export interface ChartDataset {
  label: string;
  data: number[];
  borderColor?: string;
  backgroundColor?: string;
  fill?: boolean;
  stack?: string;
  yAxisID?: string;
}

export interface ChartData {
  labels: string[];
  datasets: ChartDataset[];
}

export interface ChartOptions {
  responsive: boolean;
  plugins: {
    legend: {
      position: 'top' | 'bottom' | 'left' | 'right';
      display: boolean;
    };
    title: {
      display: boolean;
      text: string;
    };
    tooltip: {
      callbacks?: {
        label?: (context: any) => string;
      };
    };
  };
  scales?: {
    y?: {
      beginAtZero?: boolean;
      title?: {
        display?: boolean;
        text?: string;
      };
      stacked?: boolean;
    };
    y1?: {
      position?: 'left' | 'right';
      beginAtZero?: boolean;
      title?: {
        display?: boolean;
        text?: string;
      };
      grid?: {
        drawOnChartArea?: boolean;
      };
    };
    x?: {
      stacked?: boolean;
    };
  };
}

export interface MetricSummary {
  id: number;
  name: string;
  display_name: string;
  latest_value: number;
  unit: string;
  yearly_change?: number;
  yearly_change_percent?: number;
  increasing?: boolean;
  chart_data?: ChartData;
}

export interface FilterOptions {
  years: number[];
  metrics: Metric[];
}

export type { 
  Metric, 
  YearlyData, 
  MetricWithData, 
  Report, 
  ReportWithMetrics,
  ShareholderData,
  ShareholdersResponse 
}; 