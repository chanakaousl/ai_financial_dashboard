import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import apiServices from '../api/services';
import LineChart from '../components/LineChart';
import DashboardCard from '../components/DashboardCard';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import { FinancialMetric, TrendAnalysis } from '../api/services';
import { DocumentArrowDownIcon, ArrowPathIcon } from '@heroicons/react/24/outline';

const MetricDetail = () => {
  const { id } = useParams<{ id: string }>();
  const metricId = parseInt(id || '0');
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [metric, setMetric] = useState<FinancialMetric | null>(null);
  const [trendAnalysis, setTrendAnalysis] = useState<TrendAnalysis | null>(null);

  useEffect(() => {
    const fetchMetricData = async () => {
      setLoading(true);
      setError(null);
      try {
        // Fetch metric details
        const metricResponse = await apiServices.getMetricById(metricId);
        setMetric(metricResponse.data);
        
        // Fetch trend analysis
        const trendResponse = await apiServices.getMetricTrend(metricId);
        setTrendAnalysis(trendResponse.data);
      } catch (err) {
        setError(`Failed to load metric details. Please try again.`);
        console.error(err);
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
    if (metric?.unit === '%') {
      return `${value.toFixed(2)}%`;
    } else if (metric?.unit === 'LKR') {
      return `LKR ${value.toLocaleString()}`;
    } else if (metric?.unit === 'LKR/share') {
      return `LKR ${value.toLocaleString()} per share`;
    } else {
      return value.toLocaleString();
    }
  };

  const handleExportCsv = () => {
    if (metricId) {
      apiServices.exportMetricCsv(metricId);
    }
  };

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error} onRetry={() => window.location.reload()} />;
  if (!metric) return <ErrorMessage message="Metric not found" />;

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold">{metric.name}</h1>
          <p className="text-gray-600">{metric.description}</p>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={handleExportCsv}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            <DocumentArrowDownIcon className="h-5 w-5 mr-2" />
            Export CSV
          </button>
          <Link
            to="/compare"
            className="flex items-center px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300"
          >
            <ArrowPathIcon className="h-5 w-5 mr-2" />
            Compare with others
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 mb-8">
        {/* Main Trend Chart */}
        <DashboardCard title={`${metric.name} Trend (5-Year)`}>
          {metric.yearly_data && metric.yearly_data.length > 0 ? (
            <LineChart
              title=""
              labels={metric.yearly_data.map((d) => d.year)}
              datasets={[
                {
                  label: metric.name,
                  data: metric.yearly_data.map((d) => d.value),
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
      </div>

      {trendAnalysis && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* Growth Stats */}
          <DashboardCard title="Growth Analysis">
            <div className="space-y-4">
              {trendAnalysis.analysis.growth && (
                <>
                  <div>
                    <span className="block text-sm text-gray-500">Compound Annual Growth Rate</span>
                    <span className={`text-xl font-semibold ${trendAnalysis.analysis.growth.cagr >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {(trendAnalysis.analysis.growth.cagr * 100).toFixed(2)}%
                    </span>
                  </div>
                  <div>
                    <span className="block text-sm text-gray-500">Total Change</span>
                    <span className={`text-xl font-semibold ${trendAnalysis.analysis.growth.total_change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {(trendAnalysis.analysis.growth.total_change * 100).toFixed(2)}%
                    </span>
                  </div>
                </>
              )}
              
              {trendAnalysis.analysis.trend_line && (
                <div>
                  <span className="block text-sm text-gray-500">Trend Strength (R²)</span>
                  <span className="text-xl font-semibold">
                    {trendAnalysis.analysis.trend_line.r_squared.toFixed(2)}
                  </span>
                  <p className="text-xs text-gray-500 mt-1">
                    {trendAnalysis.analysis.trend_line.r_squared > 0.7 
                      ? 'Strong trend'
                      : trendAnalysis.analysis.trend_line.r_squared > 0.3
                      ? 'Moderate trend'
                      : 'Weak trend'
                    }
                  </p>
                </div>
              )}
            </div>
          </DashboardCard>
          
          {/* YoY Changes */}
          <DashboardCard title="Year-over-Year Changes">
            {trendAnalysis.analysis.yoy_changes && trendAnalysis.analysis.yoy_changes.length > 0 ? (
              <div className="space-y-3">
                {trendAnalysis.analysis.yoy_changes.map((change) => (
                  <div key={change.year} className="flex justify-between items-center">
                    <span className="font-medium">{change.year}</span>
                    <span className={`font-semibold ${change.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {(change.change * 100).toFixed(2)}%
                    </span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="py-6 text-center text-gray-500">No YoY data available</div>
            )}
          </DashboardCard>
          
          {/* Anomalies */}
          <DashboardCard title="Anomalies & Events">
            {trendAnalysis.analysis.anomalies && trendAnalysis.analysis.anomalies.length > 0 ? (
              <div className="space-y-4">
                {trendAnalysis.analysis.anomalies.map((anomaly, index) => (
                  <div key={index} className="border-l-4 border-yellow-500 pl-3 py-1">
                    <div className="font-medium">Year {anomaly.year}</div>
                    <div className="text-sm text-gray-600">{anomaly.message}</div>
                    <div className="text-xs text-gray-500 mt-1">
                      Value: {formatValue(anomaly.value)}, Change: {(anomaly.yoy_change * 100).toFixed(2)}%
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="py-6 text-center text-gray-500">No anomalies detected</div>
            )}
          </DashboardCard>
        </div>
      )}
      
      {/* Data Table */}
      <DashboardCard title="Historical Data">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Year</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Value</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Notes</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {metric.yearly_data && metric.yearly_data.length > 0 ? (
                metric.yearly_data
                  .slice() // Create a copy
                  .sort((a, b) => b.year - a.year) // Sort by descending year
                  .map((data) => (
                    <tr key={data.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{data.year}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{formatValue(data.value)}</td>
                      <td className="px-6 py-4 text-sm text-gray-500">{data.notes || '-'}</td>
                    </tr>
                  ))
              ) : (
                <tr>
                  <td colSpan={3} className="px-6 py-4 text-center text-sm text-gray-500">No data available</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </DashboardCard>
    </div>
  );
};

export default MetricDetail; 