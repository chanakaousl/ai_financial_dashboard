import { useState, useEffect } from 'react';
import apiServices from '../api/services';
import DashboardCard from '../components/DashboardCard';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorMessage from '../components/ErrorMessage';

interface ShareholderData {
  shareholder_name: string;
  number_of_shares: number;
  percentage_holding: number;
  rank: number;
}

const Shareholders = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [shareholderData, setShareholderData] = useState<Record<number, ShareholderData[]>>({});
  const [years, setYears] = useState<number[]>([]);
  const [selectedYear, setSelectedYear] = useState<number | null>(null);
  
  useEffect(() => {
    const fetchShareholdersData = async () => {
      setLoading(true);
      setError(null);
      try {
        // This is a placeholder - the API doesn't currently return structured shareholder data
        // When implemented, this will fetch actual data from the API
        
        // Try fetching from the API first
        const response = await apiServices.getShareholdersData();
        
        // Process the data if it exists, otherwise use mock data
        if (response.data?.yearly_data?.length > 0) {
          const parsedData: Record<number, ShareholderData[]> = {};
          const yearSet = new Set<number>();
          
          response.data.yearly_data.forEach(yearData => {
            // If we have parsed data for this year, use it
            if (yearData.parsed_data && Array.isArray(yearData.parsed_data)) {
              // Format might vary - adjust parsing as needed
              // This is just an example
              const shareholders = yearData.parsed_data.map((line, index) => {
                // Attempt to parse a line like "John Doe Ltd 1,234,567 12.34%"
                const parts = line.split(/\s+/);
                const percentageMatch = parts[parts.length - 1].match(/(\d+\.\d+)%?/);
                const sharesMatch = parts[parts.length - 2].replace(/,/g, '').match(/(\d+)/);
                
                // Extract shareholder name (everything before the last two elements)
                const nameEndIndex = parts.length - 2;
                const name = parts.slice(0, nameEndIndex).join(' ');
                
                return {
                  rank: index + 1,
                  shareholder_name: name,
                  number_of_shares: sharesMatch ? parseInt(sharesMatch[1]) : 0,
                  percentage_holding: percentageMatch ? parseFloat(percentageMatch[1]) : 0
                };
              });
              
              parsedData[yearData.year] = shareholders;
              yearSet.add(yearData.year);
            }
          });
          
          if (Object.keys(parsedData).length > 0) {
            setShareholderData(parsedData);
            const yearList = Array.from(yearSet).sort();
            setYears(yearList);
            setSelectedYear(yearList[yearList.length - 1]); // Select most recent year
          } else {
            // If no data could be parsed from API response, use mock data
            generateMockData();
          }
        } else {
          // If no data from API, use mock data for demonstration
          generateMockData();
        }
      } catch (err) {
        console.error("Error fetching shareholder data:", err);
        // Still show mock data for demonstration purposes
        generateMockData();
      } finally {
        setLoading(false);
      }
    };
    
    const generateMockData = () => {
      // Mock data for demonstration purposes
      const mockYears = [2019, 2020, 2021, 2022, 2023];
      const mockData: Record<number, ShareholderData[]> = {};
      
      mockYears.forEach(year => {
        mockData[year] = [
          { rank: 1, shareholder_name: "John Keells Holdings PLC - Employees Provident Fund", number_of_shares: 58326834, percentage_holding: 12.83 },
          { rank: 2, shareholder_name: "Employees Trust Fund Board", number_of_shares: 45324123, percentage_holding: 9.97 },
          { rank: 3, shareholder_name: "Ceylon Investment PLC", number_of_shares: 32145678, percentage_holding: 7.07 },
          { rank: 4, shareholder_name: "National Savings Bank", number_of_shares: 21678453, percentage_holding: 4.77 },
          { rank: 5, shareholder_name: "HSBC International Nominees Ltd", number_of_shares: 18765432, percentage_holding: 4.13 },
          { rank: 6, shareholder_name: "Bank of Ceylon", number_of_shares: 15762983, percentage_holding: 3.47 },
          { rank: 7, shareholder_name: "Citibank New York", number_of_shares: 14295673, percentage_holding: 3.14 },
          { rank: 8, shareholder_name: "Sri Lanka Insurance Corporation Ltd", number_of_shares: 11876523, percentage_holding: 2.61 },
          { rank: 9, shareholder_name: "Northern Trust Company", number_of_shares: 9854321, percentage_holding: 2.17 },
          { rank: 10, shareholder_name: "DFCC Bank PLC", number_of_shares: 8756321, percentage_holding: 1.93 },
          { rank: 11, shareholder_name: "Hatton National Bank PLC", number_of_shares: 7534621, percentage_holding: 1.66 },
          { rank: 12, shareholder_name: "Mercantile Investments Ltd", number_of_shares: 6721345, percentage_holding: 1.48 },
          { rank: 13, shareholder_name: "Ceylon Guardian Investment Trust PLC", number_of_shares: 5983241, percentage_holding: 1.32 },
          { rank: 14, shareholder_name: "Mellon Bank", number_of_shares: 5123456, percentage_holding: 1.13 },
          { rank: 15, shareholder_name: "Akbar Brothers Pvt Ltd", number_of_shares: 4756123, percentage_holding: 1.05 },
          { rank: 16, shareholder_name: "Commercial Bank of Ceylon PLC", number_of_shares: 4231456, percentage_holding: 0.93 },
          { rank: 17, shareholder_name: "Dialog Axiata PLC", number_of_shares: 3785634, percentage_holding: 0.83 },
          { rank: 18, shareholder_name: "Sampath Bank PLC", number_of_shares: 3452167, percentage_holding: 0.76 },
          { rank: 19, shareholder_name: "People's Bank", number_of_shares: 3124567, percentage_holding: 0.69 },
          { rank: 20, shareholder_name: "National Development Bank PLC", number_of_shares: 2856732, percentage_holding: 0.63 }
        ];
        
        // Slightly modify the data for each year to show some changes
        if (year > 2019) {
          mockData[year] = mockData[year].map(shareholder => {
            const changePercent = (Math.random() * 0.2) - 0.1; // -10% to +10% change
            const newShares = Math.round(shareholder.number_of_shares * (1 + changePercent));
            return {
              ...shareholder,
              number_of_shares: newShares,
              percentage_holding: shareholder.percentage_holding * (1 + changePercent/2)
            };
          });
          
          // Randomly swap a few positions for each year to simulate changing ranks
          const pos1 = Math.floor(Math.random() * 10) + 5;
          const pos2 = Math.floor(Math.random() * 10) + 5;
          if (pos1 !== pos2) {
            [mockData[year][pos1], mockData[year][pos2]] = [mockData[year][pos2], mockData[year][pos1]];
            // Update ranks
            mockData[year] = mockData[year].map((s, i) => ({ ...s, rank: i + 1 }));
          }
        }
      });
      
      setShareholderData(mockData);
      setYears(mockYears);
      setSelectedYear(2023); // Most recent year
    };
    
    fetchShareholdersData();
  }, []);
  
  const formatNumber = (num: number) => {
    return num.toLocaleString();
  };
  
  const calculateTotalShares = (data: ShareholderData[]) => {
    return data.reduce((sum, shareholder) => sum + shareholder.number_of_shares, 0);
  };
  
  const calculateTotalPercentage = (data: ShareholderData[]) => {
    return data.reduce((sum, shareholder) => sum + shareholder.percentage_holding, 0);
  };
  
  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error} onRetry={() => window.location.reload()} />;
  
  // Get data for selected year
  const currentYearData = selectedYear ? shareholderData[selectedYear] : null;
  
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Top 20 Shareholders</h1>
        <div className="flex items-center space-x-2">
          <span>Select Year:</span>
          <select
            value={selectedYear || ''}
            onChange={(e) => setSelectedYear(parseInt(e.target.value))}
            className="border rounded p-2"
          >
            {years.map((year) => (
              <option key={year} value={year}>
                {year}
              </option>
            ))}
          </select>
        </div>
      </div>
      
      <div className="grid grid-cols-1 gap-6">
        <DashboardCard title={`Shareholder Analysis - ${selectedYear}`}>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Rank</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Shareholder Name</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Number of Shares</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">% Holding</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {currentYearData && currentYearData.length > 0 ? (
                  <>
                    {currentYearData.map((shareholder) => (
                      <tr key={shareholder.rank} className={shareholder.rank <= 5 ? 'bg-blue-50' : ''}>
                        <td className="px-6 py-3 whitespace-nowrap text-sm font-medium text-gray-900">{shareholder.rank}</td>
                        <td className="px-6 py-3 text-sm text-gray-900">{shareholder.shareholder_name}</td>
                        <td className="px-6 py-3 text-right whitespace-nowrap text-sm text-gray-500">{formatNumber(shareholder.number_of_shares)}</td>
                        <td className="px-6 py-3 text-right whitespace-nowrap text-sm text-gray-900">{shareholder.percentage_holding.toFixed(2)}%</td>
                      </tr>
                    ))}
                    <tr className="bg-gray-100 font-semibold">
                      <td className="px-6 py-3 whitespace-nowrap text-sm text-gray-900" colSpan={2}>Total (Top 20 Shareholders)</td>
                      <td className="px-6 py-3 text-right whitespace-nowrap text-sm text-gray-900">{formatNumber(calculateTotalShares(currentYearData))}</td>
                      <td className="px-6 py-3 text-right whitespace-nowrap text-sm text-gray-900">{calculateTotalPercentage(currentYearData).toFixed(2)}%</td>
                    </tr>
                  </>
                ) : (
                  <tr>
                    <td colSpan={4} className="px-6 py-4 text-center text-sm text-gray-500">No shareholder data available for this year</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </DashboardCard>
        
        <div className="text-sm text-gray-500 italic mt-2">
          <p>Note: This is simulated shareholder data for demonstration purposes. In a production environment, this data would be extracted from the financial reports.</p>
        </div>
        
        {currentYearData && currentYearData.length > 0 && (
          <DashboardCard title="Ownership Analysis">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="font-semibold mb-3">Ownership Concentration</h3>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Top 5 Shareholders</span>
                    <span className="font-medium">
                      {calculateTotalPercentage(currentYearData.slice(0, 5)).toFixed(2)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded">
                    <div 
                      className="bg-blue-600 rounded h-2" 
                      style={{ width: `${calculateTotalPercentage(currentYearData.slice(0, 5))}%` }}
                    ></div>
                  </div>
                  
                  <div className="flex justify-between mt-4">
                    <span>Top 10 Shareholders</span>
                    <span className="font-medium">
                      {calculateTotalPercentage(currentYearData.slice(0, 10)).toFixed(2)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded">
                    <div 
                      className="bg-green-600 rounded h-2" 
                      style={{ width: `${calculateTotalPercentage(currentYearData.slice(0, 10))}%` }}
                    ></div>
                  </div>
                  
                  <div className="flex justify-between mt-4">
                    <span>All Top 20 Shareholders</span>
                    <span className="font-medium">
                      {calculateTotalPercentage(currentYearData).toFixed(2)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded">
                    <div 
                      className="bg-purple-600 rounded h-2" 
                      style={{ width: `${calculateTotalPercentage(currentYearData)}%` }}
                    ></div>
                  </div>
                </div>
              </div>
              
              <div>
                <h3 className="font-semibold mb-3">Ownership Type Distribution</h3>
                <div className="space-y-2">
                  {/* In a real application, this would categorize shareholders by type */}
                  <div className="flex justify-between">
                    <span>Institutional Investors</span>
                    <span className="font-medium">62.5%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded">
                    <div className="bg-blue-500 rounded h-2" style={{ width: '62.5%' }}></div>
                  </div>
                  
                  <div className="flex justify-between mt-4">
                    <span>Individual Investors</span>
                    <span className="font-medium">22.3%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded">
                    <div className="bg-green-500 rounded h-2" style={{ width: '22.3%' }}></div>
                  </div>
                  
                  <div className="flex justify-between mt-4">
                    <span>Government Entities</span>
                    <span className="font-medium">13.5%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded">
                    <div className="bg-yellow-500 rounded h-2" style={{ width: '13.5%' }}></div>
                  </div>
                  
                  <div className="flex justify-between mt-4">
                    <span>Foreign Investors</span>
                    <span className="font-medium">1.7%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded">
                    <div className="bg-red-500 rounded h-2" style={{ width: '1.7%' }}></div>
                  </div>
                </div>
              </div>
            </div>
          </DashboardCard>
        )}
      </div>
    </div>
  );
};

export default Shareholders; 