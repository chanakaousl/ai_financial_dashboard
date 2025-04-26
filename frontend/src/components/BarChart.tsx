import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ChartOptions,
} from 'chart.js';
import { useEffect, useState } from 'react';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface BarChartProps {
  title: string;
  labels: (string | number)[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor?: string;
    borderColor?: string;
    borderWidth?: number;
    stack?: string;
  }[];
  yAxisLabel?: string;
  stacked?: boolean;
  tooltipCallback?: (value: number) => string;
  horizontal?: boolean;
}

const BarChart = ({ 
  title, 
  labels, 
  datasets, 
  yAxisLabel, 
  stacked = false,
  tooltipCallback,
  horizontal = false
}: BarChartProps) => {
  const [isDarkMode, setIsDarkMode] = useState(false);

  // Check if dark mode is active
  useEffect(() => {
    const checkDarkMode = () => {
      setIsDarkMode(document.documentElement.classList.contains('dark'));
    };
    
    // Initial check
    checkDarkMode();
    
    // Watch for theme changes
    const observer = new MutationObserver(checkDarkMode);
    observer.observe(document.documentElement, { 
      attributes: true, 
      attributeFilter: ['class'] 
    });
    
    return () => observer.disconnect();
  }, []);

  const options: ChartOptions<'bar'> = {
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: horizontal ? 'y' : 'x',
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: isDarkMode ? '#f3f4f6' : '#374151',
          font: {
            weight: 'bold'
          }
        }
      },
      title: {
        display: true,
        text: title,
        color: isDarkMode ? '#ffffff' : '#111827',
        font: {
          size: 16,
          weight: 'bold',
        },
      },
      tooltip: {
        backgroundColor: isDarkMode ? '#374151' : '#ffffff',
        titleColor: isDarkMode ? '#ffffff' : '#111827',
        bodyColor: isDarkMode ? '#f3f4f6' : '#4b5563',
        borderColor: isDarkMode ? '#4b5563' : '#e5e7eb',
        borderWidth: 1,
        callbacks: {
          label: function(context) {
            let label = context.dataset.label || '';
            if (label) {
              label += ': ';
            }
            if (context.parsed.y !== null) {
              const value = horizontal ? context.parsed.x : context.parsed.y;
              label += tooltipCallback ? tooltipCallback(value) : value;
            }
            return label;
          }
        }
      }
    },
    scales: {
      x: {
        stacked,
        ticks: {
          color: isDarkMode ? '#d1d5db' : '#6b7280',
        },
        grid: {
          color: isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
        }
      },
      y: {
        stacked,
        title: {
          display: !!yAxisLabel,
          text: yAxisLabel,
          color: isDarkMode ? '#f3f4f6' : '#4b5563',
        },
        ticks: {
          color: isDarkMode ? '#d1d5db' : '#6b7280',
          callback: function(value) {
            return tooltipCallback ? tooltipCallback(value as number) : value;
          }
        },
        grid: {
          color: isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
        }
      },
    },
  };

  const chartData = {
    labels,
    datasets: datasets.map(dataset => ({
      label: dataset.label,
      data: dataset.data,
      backgroundColor: dataset.backgroundColor || 'rgba(53, 162, 235, 0.5)',
      borderColor: dataset.borderColor || 'rgb(53, 162, 235)',
      borderWidth: dataset.borderWidth || 1,
      stack: dataset.stack,
    })),
  };

  return (
    <div className="h-80 w-full">
      <Bar options={options} data={chartData} />
    </div>
  );
};

export default BarChart; 