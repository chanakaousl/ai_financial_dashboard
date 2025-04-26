import { useState, useEffect } from 'react';
import apiServices from '../api/services';
import LineChart from '../components/LineChart';
import DashboardCard from '../components/DashboardCard';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import { FinancialMetric } from '../api/services';
import { DocumentArrowDownIcon } from '@heroicons/react/24/outline';

const CompareMetrics = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [metrics, setMetrics] = useState<FinancialMetric[]>([]);
  const [selectedMetricIds, setSelectedMetricIds] = useState<number[]>([1, 3]); // Default: Revenue, Operating Expenses
  const [selectedMetrics, setSelectedMetrics] = useState<FinancialMetric[]>([]);
  const [normalized, setNormalized] = useState(false);
  const [showPercentageChange, setShowPercentageChange] = useState(false);

  useEffect(() => {
    const fetchMetrics = async () => {
      setLoading(true);
      setError(null);
      try {
        const metricsResponse = await apiServices.getAllMetrics();
        setMetrics(metricsResponse.data);
      } catch (err) {
        setError('Failed to load metrics. Please try again.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
  }, []);

  useEffect(() => {
    const fetchSelectedMetricsData = async () => {
      setLoading(true);
      try {
        const selectedMetricsData = await Promise.all(
          selectedMetricIds.map(id => apiServices.getMetricById(id))
        );
        setSelectedMetrics(selectedMetricsData.map(response => response.data));
      } catch (err) {
        setError('Failed to load selected metrics data.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    if (selectedMetricIds.length > 0) {
      fetchSelectedMetricsData();
    } else {
      setSelectedMetrics([]);
      setLoading(false);
    }
  }, [selectedMetricIds]);

  const handleMetricToggle = (id: number) => {
    setSelectedMetricIds(prev => {
      if (prev.includes(id)) {
        return prev.filter(metricId => metricId !== id);
      } else {
        return [...prev, id];
      }
    });
  };

  const calculatePercentageChange = (data: number[]) => {
    if (data.length < 2) return [];
    const baseValue = data[0];
    return data.map(value => ((value - baseValue) / Math.abs(baseValue)) * 100);
  };

  const formatValue = (value: number, unit: string) => {
    if (unit === '%' || showPercentageChange) {
      return `${value.toFixed(2)}%`;
    } else if (unit === 'LKR') {
      return `LKR ${value.toLocaleString()}`;
    } else if (unit === 'LKR/share') {
      return `LKR ${value.toLocaleString()} per share`;
    } else {
      return value.toLocaleString();
    }
  };

  const handleExportCsv = () => {
    if (selectedMetricIds.length > 0) {
      apiServices.exportCompareCsv(selectedMetricIds);
    }
  };

  const normalizeValue = (value: number, baseValue: number) => {
    return (value / baseValue) * 100;
  };

  // Get all years from selected metrics and organize data for chart
  const prepareChartData = () => {
    if (selectedMetrics.length === 0) return { labels: [], datasets: [] };

    // Get all years from all selected metrics
    const allYears = new Set<number>();
    selectedMetrics.forEach(metric => {
      metric.yearly_data?.forEach(data => {
        allYears.add(data.year);
      });
    });

    // Sort years
    const sortedYears = Array.from(allYears).sort((a, b) => a - b);

    // Prepare datasets
    const datasets = selectedMetrics.map(metric => {
      // Create a map of year to value for easier access
      const yearValueMap: Record<number, number> = {};
      metric.yearly_data?.forEach(data => {
        yearValueMap[data.year] = data.value;
      });

      // Get values for all years, using null for missing years
      const values = sortedYears.map(year => {
        return yearValueMap[year] !== undefined ? yearValueMap[year] : null;
      });

      // Filter out null values (years without data)
      const validValues = values.filter(v => v !== null) as number[];

      // Apply normalization or percentage change if selected
      let processedValues = values;
      if (validValues.length > 0) {
        if (normalized) {
          const baseValue = validValues[0]; // First year as base
          processedValues = values.map(v => {
            return v !== null ? normalizeValue(v, baseValue) : null;
          });
        } else if (showPercentageChange) {
          const baseValue = validValues[0]; // First year as base
          processedValues = values.map(v => {
            return v !== null ? ((v - baseValue) / Math.abs(baseValue)) * 100 : null;
          });
        }
      }

      // Generate a random color for each dataset
      const r = Math.floor(Math.random() * 200) + 55;
      const g = Math.floor(Math.random() * 200) + 55;
      const b = Math.floor(Math.random() * 200) + 55;
      const borderColor = `rgb(${r}, ${g}, ${b})`;
      const backgroundColor = `rgba(${r}, ${g}, ${b}, 0.5)`;

      return {
        label: metric.name,
        data: processedValues,
        borderColor,
        backgroundColor,
      };
    });

    return { labels: sortedYears, datasets };
  };

  const chartData = prepareChartData();

  const getYAxisLabel = () => {
    if (normalized) {
      return 'Indexed Value (First Year = 100)';
    } else if (showPercentageChange) {
      return 'Percentage Change (%)';
    } else if (selectedMetrics.length === 1) {
      return selectedMetrics[0].unit;
    } else {
      return '';
    }
  };

  const getTooltipCallback = () => {
    if (normalized) {
      return (value: number) => `${value.toFixed(2)}%`;
    } else if (showPercentageChange) {
      return (value: number) => `${value.toFixed(2)}%`;
    } else if (selectedMetrics.length === 1) {
      return (value: number) => formatValue(value, selectedMetrics[0].unit);
    } else {
      return (value: number) => value.toLocaleString();
    }
  };

  if (loading && metrics.length === 0) return <LoadingSpinner />;
  if (error && metrics.length === 0) return <ErrorMessage message={error} onRetry={() => window.location.reload()} />;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Compare Financial Metrics</h1>
        <button
          onClick={handleExportCsv}
          disabled={selectedMetricIds.length === 0}
          className={`flex items-center px-4 py-2 rounded ${
            selectedMetricIds.length > 0
              ? 'bg-blue-600 text-white hover:bg-blue-700'
              : 'bg-gray-200 text-gray-500 cursor-not-allowed'
          }`}
        >
          <DocumentArrowDownIcon className="h-5 w-5 mr-2" />
          Export Comparison
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-8">
        <div className="lg:col-span-1">
          <DashboardCard title="Select Metrics">
            <div className="space-y-4">
              <div className="mb-4">
                <p className="text-sm text-gray-600 mb-2">
                  Select metrics to compare. Choose metrics with similar scales or use normalization for better visualization.
                </p>
                <div className="flex items-center space-x-2 mb-4">
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={normalized}
                      onChange={() => {
                        setNormalized(!normalized);
                        if (!normalized) setShowPercentageChange(false);
                      }}
                      className="mr-2"
                    />
                    <span className="text-sm">Normalize values</span>
                  </label>
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={showPercentageChange}
                      onChange={() => {
                        setShowPercentageChange(!showPercentageChange);
                        if (!showPercentageChange) setNormalized(false);
                      }}
                      className="mr-2"
                    />
                    <span className="text-sm">Show % change</span>
                  </label>
                </div>
              </div>

              {loading ? (
                <div className="py-4">
                  <LoadingSpinner />
                </div>
              ) : (
                <div className="max-h-96 overflow-y-auto pr-2">
                  {metrics.map(metric => (
                    <div
                      key={metric.id}
                      className={`p-3 mb-2 rounded-md cursor-pointer border ${
                        selectedMetricIds.includes(metric.id)
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                      onClick={() => handleMetricToggle(metric.id)}
                    >
                      <div className="font-medium">{metric.name}</div>
                      <div className="text-xs text-gray-500">{metric.unit}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </DashboardCard>
        </div>

        <div className="lg:col-span-3">
          <DashboardCard title="Comparison Chart">
            {error && <ErrorMessage message={error} />}
            
            {selectedMetrics.length === 0 ? (
              <div className="py-20 text-center text-gray-500">
                Select at least one metric to display the chart
              </div>
            ) : loading ? (
              <LoadingSpinner />
            ) : (
              <LineChart
                title=""
                labels={chartData.labels}
                datasets={chartData.datasets}
                yAxisLabel={getYAxisLabel()}
                tooltipCallback={getTooltipCallback()}
              />
            )}
          </DashboardCard>

          {selectedMetrics.length > 0 && (
            <div className="mt-6">
              <DashboardCard title="Selected Metrics Summary">
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Metric
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Latest Value
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Change (5Y)
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Unit
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {selectedMetrics.map(metric => {
                        const yearlyData = metric.yearly_data || [];
                        const sortedData = [...yearlyData].sort((a, b) => a.year - b.year);
                        
                        const firstValue = sortedData[0]?.value;
                        const lastValue = sortedData[sortedData.length - 1]?.value;
                        const change = firstValue !== undefined && lastValue !== undefined
                          ? ((lastValue - firstValue) / Math.abs(firstValue)) * 100
                          : null;
                        
                        return (
                          <tr key={metric.id}>
                            <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                              {metric.name}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {lastValue !== undefined
                                ? formatValue(lastValue, metric.unit)
                                : '-'}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {change !== null ? (
                                <span className={change >= 0 ? 'text-green-600' : 'text-red-600'}>
                                  {change >= 0 ? '+' : ''}{change.toFixed(2)}%
                                </span>
                              ) : '-'}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                              {metric.unit}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </DashboardCard>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CompareMetrics; 