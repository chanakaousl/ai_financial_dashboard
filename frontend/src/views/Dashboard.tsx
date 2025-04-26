import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import apiServices from '../api/services';
import LineChart from '../components/LineChart';
import BarChart from '../components/BarChart';
import DashboardCard from '../components/DashboardCard';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';
import { ArrowUpIcon, ArrowDownIcon } from '@heroicons/react/24/solid';

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [metrics, setMetrics] = useState<any[]>([]);
  const [revenueData, setRevenueData] = useState<any>(null);
  const [epsData, setEpsData] = useState<any>(null);
  const [navData, setNavData] = useState<any>(null);
  const [profitMarginData, setProfitMarginData] = useState<any>(null);
  const [expensesData, setExpensesData] = useState<any>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      setError(null);
      try {
        // Fetch all metrics
        const metricsResponse = await apiServices.getAllMetrics();
        setMetrics(metricsResponse.data);

        // Fetch Revenue data (assuming metric ID 1 is revenue)
        const revenueResponse = await apiServices.getMetricById(1);
        setRevenueData(revenueResponse.data);

        // Fetch EPS data (assuming metric ID 5 is EPS)
        const epsResponse = await apiServices.getMetricById(5);
        setEpsData(epsResponse.data);

        // Fetch NAV data (assuming metric ID 6 is Net Asset Value per share)
        const navResponse = await apiServices.getMetricById(6);
        setNavData(navResponse.data);

        // Fetch Gross Profit Margin data (assuming metric ID 4 is Gross Profit Margin)
        const profitMarginResponse = await apiServices.getMetricById(4);
        setProfitMarginData(profitMarginResponse.data);

        // Fetch Operating Expenses data (assuming metric ID 3 is Operating Expenses)
        const expensesResponse = await apiServices.getMetricById(3);
        setExpensesData(expensesResponse.data);

      } catch (err) {
        setError('Failed to load dashboard data. Please try again.');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const formatValue = (value: number, unit: string) => {
    if (unit === '%') {
      return `${value.toFixed(2)}%`;
    } else if (unit === 'LKR') {
      return `LKR ${value.toLocaleString()}`;
    } else {
      return value.toLocaleString();
    }
  };

  const getValueTrend = (data: any) => {
    if (!data?.yearly_data || data.yearly_data.length < 2) return null;
    
    const sortedData = [...data.yearly_data].sort((a, b) => a.year - b.year);
    const latestValue = sortedData[sortedData.length - 1].value;
    const previousValue = sortedData[sortedData.length - 2].value;
    const change = latestValue - previousValue;
    const percentChange = (change / Math.abs(previousValue)) * 100;
    
    return {
      value: latestValue,
      change,
      percentChange,
      increasing: change > 0
    };
  };

  const renderMetricTrend = (data: any) => {
    const trend = getValueTrend(data);
    if (!trend) return null;
    
    return (
      <div className="flex items-center">
        <span className={`font-bold ${trend.increasing ? 'text-green-600' : 'text-red-600'}`}>
          {trend.increasing ? '+' : ''}{formatValue(trend.change, data.unit)}
        </span>
        <span className={`ml-1 flex items-center ${trend.increasing ? 'text-green-600' : 'text-red-600'}`}>
          {trend.increasing ? (
            <ArrowUpIcon className="h-4 w-4 mr-1" />
          ) : (
            <ArrowDownIcon className="h-4 w-4 mr-1" />
          )}
          {Math.abs(trend.percentChange).toFixed(2)}%
        </span>
      </div>
    );
  };

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error} onRetry={() => window.location.reload()} />;

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">John Keells Holdings Financial Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {/* Revenue Card */}
        {revenueData && (
          <DashboardCard 
            title="Total Revenue" 
            className="bg-gradient-to-br from-blue-50 to-blue-100"
            actions={<Link to="/metrics/1" className="text-blue-600 hover:underline text-sm">View Details</Link>}
          >
            <div className="flex flex-col">
              <span className="text-3xl font-bold">
                {formatValue(revenueData.yearly_data?.slice(-1)[0]?.value || 0, revenueData.unit)}
              </span>
              {renderMetricTrend(revenueData)}
              <span className="text-gray-500 text-sm mt-2">Latest Year: {revenueData.yearly_data?.slice(-1)[0]?.year || 'N/A'}</span>
            </div>
          </DashboardCard>
        )}
        
        {/* EPS Card */}
        {epsData && (
          <DashboardCard 
            title="Earnings Per Share" 
            className="bg-gradient-to-br from-green-50 to-green-100"
            actions={<Link to="/metrics/5" className="text-green-600 hover:underline text-sm">View Details</Link>}
          >
            <div className="flex flex-col">
              <span className="text-3xl font-bold">
                {formatValue(epsData.yearly_data?.slice(-1)[0]?.value || 0, epsData.unit)}
              </span>
              {renderMetricTrend(epsData)}
              <span className="text-gray-500 text-sm mt-2">Latest Year: {epsData.yearly_data?.slice(-1)[0]?.year || 'N/A'}</span>
            </div>
          </DashboardCard>
        )}
        
        {/* Gross Profit Margin */}
        {profitMarginData && (
          <DashboardCard 
            title="Gross Profit Margin" 
            className="bg-gradient-to-br from-purple-50 to-purple-100"
            actions={<Link to="/metrics/4" className="text-purple-600 hover:underline text-sm">View Details</Link>}
          >
            <div className="flex flex-col">
              <span className="text-3xl font-bold">
                {formatValue(profitMarginData.yearly_data?.slice(-1)[0]?.value || 0, profitMarginData.unit)}
              </span>
              {renderMetricTrend(profitMarginData)}
              <span className="text-gray-500 text-sm mt-2">Latest Year: {profitMarginData.yearly_data?.slice(-1)[0]?.year || 'N/A'}</span>
            </div>
          </DashboardCard>
        )}
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Revenue Chart */}
        {revenueData && revenueData.yearly_data && (
          <DashboardCard 
            title="Revenue Trend (5-Year)" 
            actions={<Link to="/metrics/1" className="text-blue-600 hover:underline text-sm">View Details</Link>}
          >
            <LineChart 
              title="" 
              labels={revenueData.yearly_data.map((d: any) => d.year)}
              datasets={[
                {
                  label: 'Revenue',
                  data: revenueData.yearly_data.map((d: any) => d.value),
                  borderColor: 'rgb(53, 162, 235)',
                  backgroundColor: 'rgba(53, 162, 235, 0.5)',
                }
              ]}
              yAxisLabel={revenueData.unit}
              tooltipCallback={(value) => formatValue(value, revenueData.unit)}
            />
          </DashboardCard>
        )}
        
        {/* Cost vs. Expenses Chart */}
        {expensesData && revenueData && revenueData.yearly_data && (
          <DashboardCard 
            title="Cost of Sales vs. Operating Expenses" 
            actions={<Link to="/compare" className="text-blue-600 hover:underline text-sm">Compare</Link>}
          >
            <BarChart 
              title="" 
              labels={
                expensesData.yearly_data 
                  ? expensesData.yearly_data.map((d: any) => d.year) 
                  : []
              }
              datasets={[
                {
                  label: 'Cost of Sales',
                  data: metrics.find((m: any) => m.name === 'cost_of_sales')?.yearly_data?.map((d: any) => d.value) || [],
                  backgroundColor: 'rgba(255, 99, 132, 0.5)',
                  stack: 'Stack 0',
                },
                {
                  label: 'Operating Expenses',
                  data: expensesData.yearly_data?.map((d: any) => d.value) || [],
                  backgroundColor: 'rgba(75, 192, 192, 0.5)',
                  stack: 'Stack 0',
                }
              ]}
              yAxisLabel="LKR"
              stacked={true}
              tooltipCallback={(value) => `LKR ${value.toLocaleString()}`}
            />
          </DashboardCard>
        )}
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Gross Profit Margin Chart */}
        {profitMarginData && profitMarginData.yearly_data && (
          <DashboardCard 
            title="Gross Profit Margin (5-Year)" 
            actions={<Link to="/metrics/4" className="text-blue-600 hover:underline text-sm">View Details</Link>}
          >
            <LineChart 
              title="" 
              labels={profitMarginData.yearly_data.map((d: any) => d.year)}
              datasets={[
                {
                  label: 'Gross Profit Margin',
                  data: profitMarginData.yearly_data.map((d: any) => d.value),
                  borderColor: 'rgb(153, 102, 255)',
                  backgroundColor: 'rgba(153, 102, 255, 0.5)',
                  fill: true,
                }
              ]}
              yAxisLabel="%"
              tooltipCallback={(value) => `${value.toFixed(2)}%`}
            />
          </DashboardCard>
        )}
        
        {/* EPS Chart */}
        {epsData && epsData.yearly_data && (
          <DashboardCard 
            title="Earnings Per Share (5-Year)" 
            actions={<Link to="/metrics/5" className="text-blue-600 hover:underline text-sm">View Details</Link>}
          >
            <LineChart 
              title="" 
              labels={epsData.yearly_data.map((d: any) => d.year)}
              datasets={[
                {
                  label: 'EPS',
                  data: epsData.yearly_data.map((d: any) => d.value),
                  borderColor: 'rgb(75, 192, 192)',
                  backgroundColor: 'rgba(75, 192, 192, 0.5)',
                }
              ]}
              yAxisLabel={epsData.unit}
              tooltipCallback={(value) => formatValue(value, epsData.unit)}
            />
          </DashboardCard>
        )}
      </div>
    </div>
  );
};

export default Dashboard; 