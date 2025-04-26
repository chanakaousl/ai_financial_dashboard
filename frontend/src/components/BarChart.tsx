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
  const options: ChartOptions<'bar'> = {
    responsive: true,
    maintainAspectRatio: false,
    indexAxis: horizontal ? 'y' : 'x',
    plugins: {
      legend: {
        position: 'top',
      },
      title: {
        display: true,
        text: title,
        font: {
          size: 16,
          weight: 'bold',
        },
      },
      tooltip: {
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
      },
      y: {
        stacked,
        title: {
          display: !!yAxisLabel,
          text: yAxisLabel,
        },
        ticks: {
          callback: function(value) {
            return tooltipCallback ? tooltipCallback(value as number) : value;
          }
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