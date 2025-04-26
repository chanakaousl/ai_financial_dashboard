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
  const options: ChartOptions<'line'> = {
    responsive: true,
    maintainAspectRatio: false,
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