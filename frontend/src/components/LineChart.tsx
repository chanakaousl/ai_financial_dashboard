import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
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
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface LineChartProps {
  title: string;
  labels: (string | number)[];
  datasets: {
    label: string;
    data: number[];
    borderColor?: string;
    backgroundColor?: string;
    fill?: boolean;
  }[];
  yAxisLabel?: string;
  tooltipCallback?: (value: number) => string;
}

const LineChart = ({ 
  title, 
  labels, 
  datasets, 
  yAxisLabel, 
  tooltipCallback 
}: LineChartProps) => {
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

  const options: ChartOptions<'line'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: isDarkMode ? '#f3f4f6' : '#374151', // Text color for legend
          font: {
            weight: 'bold'
          }
        }
      },
      title: {
        display: true,
        text: title,
        color: isDarkMode ? '#ffffff' : '#111827', // Title text color
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
              const value = context.parsed.y;
              label += tooltipCallback ? tooltipCallback(value) : value;
            }
            return label;
          }
        }
      }
    },
    scales: {
      y: {
        title: {
          display: !!yAxisLabel,
          text: yAxisLabel,
          color: isDarkMode ? '#f3f4f6' : '#4b5563', // Y-axis title color
        },
        ticks: {
          color: isDarkMode ? '#d1d5db' : '#6b7280', // Y-axis tick color
          callback: function(value) {
            return tooltipCallback ? tooltipCallback(value as number) : value;
          }
        },
        grid: {
          color: isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)', // Grid line color
        }
      },
      x: {
        ticks: {
          color: isDarkMode ? '#d1d5db' : '#6b7280', // X-axis tick color
        },
        grid: {
          color: isDarkMode ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)', // Grid line color
        }
      }
    },
  };

  const chartData = {
    labels,
    datasets: datasets.map(dataset => ({
      label: dataset.label,
      data: dataset.data,
      borderColor: dataset.borderColor || 'rgb(53, 162, 235)',
      backgroundColor: dataset.backgroundColor || 'rgba(53, 162, 235, 0.5)',
      fill: dataset.fill !== undefined ? dataset.fill : false,
    })),
  };

  return (
    <div className="h-80 w-full">
      <Line options={options} data={chartData} />
    </div>
  );
};

export default LineChart; 