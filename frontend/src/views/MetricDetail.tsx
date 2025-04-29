import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import apiServices from '../api/services';
import LineChart from '../components/LineChart';
import DashboardCard from '../components/DashboardCard';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import { MetricWithData } from '../api/services';
import { ArrowPathIcon } from '@heroicons/react/24/outline';

const MetricDetail = () => {
  const { id } = useParams<{ id: string }>();
  const metricId = parseInt(id || '0');
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [metric, setMetric] = useState<MetricWithData | null>(null);

  useEffect(() => {
    const fetchMetricData = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await apiServices.getMetricById(metricId);
        if (response.status === 'success') {
          setMetric(response.data);
        } else {
          setError('Failed to load metric data');
        }
      } catch (err) {
        console.error('Error fetching metric:', err);
        setError('Failed to load metric details. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    if (metricId) {
      fetchMetricData();
    } else {
      setError('Invalid metric ID');
      setLoading(false);
    }
  }, [metricId]);

  const formatValue = (value: number) => {
    if (!metric) return value.toString();
    
    if (metric.unit === '%') {
      return `${value.toFixed(2)}%`;
    } else if (metric.unit === 'LKR') {
      return `LKR ${value.toLocaleString()}`;
    } else if (metric.unit === 'LKR/share') {
      return `LKR ${value.toLocaleString()} per share`;
    } else {
      return value.toLocaleString();
    }
  };

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error} onRetry={() => window.location.reload()} />;
  if (!metric) return <ErrorMessage message="Metric not found" />;

  // Sort yearly data by year in descending order
  const sortedYearlyData = [...(metric.yearly_data || [])].sort((a, b) => b.year - a.year);
  const latestYear = sortedYearlyData[0]?.year;
  const previousYear = sortedYearlyData[1]?.year;
  const latestValue = sortedYearlyData[0]?.value;
  const previousValue = sortedYearlyData[1]?.value;

  // Calculate year-over-year change
  const yearOverYearChange = latestValue && previousValue 
    ? ((latestValue - previousValue) / previousValue) * 100 
    : null;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold mb-2">{metric.name}</h1>
          <p className="text-gray-600 dark:text-gray-400">{metric.description}</p>
          {metric.category && (
            <span className="inline-block mt-2 px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-full text-sm">
              {metric.category}
            </span>
          )}
        </div>
        <div className="flex space-x-2">
          <Link
            to="/compare"
            className="flex items-center px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-200 rounded hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
          >
            <ArrowPathIcon className="h-5 w-5 mr-2" />
            Compare with others
          </Link>
        </div>
      </div>

      {latestValue && previousValue && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <DashboardCard title="Latest Value">
            <div className="text-3xl font-bold mb-2">{formatValue(latestValue)}</div>
            <div className="text-sm text-gray-500">Year {latestYear}</div>
          </DashboardCard>

          <DashboardCard title="Previous Value">
            <div className="text-2xl font-bold mb-2">{formatValue(previousValue)}</div>
            <div className="text-sm text-gray-500">Year {previousYear}</div>
          </DashboardCard>

          {yearOverYearChange !== null && (
            <DashboardCard title="Year-over-Year Change">
              <div className={`text-2xl font-bold mb-2 ${yearOverYearChange >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {yearOverYearChange >= 0 ? '+' : ''}{yearOverYearChange.toFixed(2)}%
              </div>
              <div className="text-sm text-gray-500">From {previousYear} to {latestYear}</div>
            </DashboardCard>
          )}
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 mb-8">
        {/* Trend Chart */}
        <DashboardCard title={`${metric.name} Historical Trend`}>
          {metric.yearly_data && metric.yearly_data.length > 0 ? (
            <LineChart
              title=""
              labels={metric.yearly_data.map(d => d.year)}
              datasets={[
                {
                  label: metric.name,
                  data: metric.yearly_data.map(d => d.value),
                  borderColor: 'rgb(53, 162, 235)',
                  backgroundColor: 'rgba(53, 162, 235, 0.5)',
                }
              ]}
              yAxisLabel={metric.unit}
              tooltipCallback={(value) => formatValue(value)}
            />
          ) : (
            <div className="py-6 text-center text-gray-500">No data available</div>
          )}
        </DashboardCard>

        {/* Data Table */}
        <DashboardCard title="Historical Data">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-800">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Year
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                    Value
                  </th>
                  {yearOverYearChange !== null && (
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                      YoY Change
                    </th>
                  )}
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-700">
                {sortedYearlyData.map((data, index) => {
                  const nextValue = sortedYearlyData[index + 1]?.value;
                  const yoyChange = nextValue ? ((data.value - nextValue) / nextValue) * 100 : null;
                  
                  return (
                    <tr key={data.year} className="hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-gray-100">
                        {data.year}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        {formatValue(data.value)}
                      </td>
                      {yearOverYearChange !== null && (
                        <td className="px-6 py-4 whitespace-nowrap text-sm">
                          {yoyChange !== null ? (
                            <span className={yoyChange >= 0 ? 'text-green-600' : 'text-red-600'}>
                              {yoyChange >= 0 ? '+' : ''}{yoyChange.toFixed(2)}%
                            </span>
                          ) : '-'}
                        </td>
                      )}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </DashboardCard>
      </div>
    </div>
  );
};

export default MetricDetail;