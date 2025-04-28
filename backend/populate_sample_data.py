import logging
import random
from database import db
from models.financial_data import FinancialReport, FinancialMetric, YearlyData, ShareholderData

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def populate_sample_data():
    """Populate the database with sample data for development/testing"""
    try:
        # Initialize database
        db.init_db()
        session = db.get_session()
        
        # Check if data already exists
        reports_count = session.query(FinancialReport).count()
        if reports_count > 0:
            logger.info("Database already contains data. Skipping sample data generation.")
            return
        
        logger.info("Populating database with sample data...")
        
        # Create financial reports for 5 years (2020-2024)
        reports = []
        for year in range(2020, 2025):
            report = FinancialReport(
                year=year,
                pdf_path=f"data-pdf/508_{1590052852777 + (year-2020)*31796230}.pdf"
            )
            reports.append(report)
        
        db.bulk_add_and_commit(session, reports)
        logger.info(f"Created {len(reports)} financial reports")
        
        # Get all reports and metrics
        reports = session.query(FinancialReport).all()
        metrics = session.query(FinancialMetric).all()
        
        # Create sample data for each metric and report
        yearly_data = []
        
        # Revenue data with growth
        revenue_metric = next((m for m in metrics if m.name == "revenue"), None)
        base_revenue = 130000000000.0  # 130 billion LKR
        for i, report in enumerate(reports):
            # Revenue grows by 8-15% each year, except 2020 which saw decline due to COVID
            growth_rate = -0.12 if report.year == 2020 else random.uniform(0.08, 0.15)
            revenue_value = base_revenue * (1 + growth_rate) ** i
            yearly_data.append(YearlyData(
                report_id=report.id,
                metric_id=revenue_metric.id,
                value=revenue_value
            ))
        
        # Cost of Sales data (typically 75-80% of revenue)
        cost_metric = next((m for m in metrics if m.name == "cost_of_sales"), None)
        for i, report in enumerate(reports):
            revenue_data = next((d for d in yearly_data if d.report_id == report.id and d.metric_id == revenue_metric.id), None)
            cost_ratio = random.uniform(0.75, 0.80)
            cost_value = revenue_data.value * cost_ratio
            yearly_data.append(YearlyData(
                report_id=report.id,
                metric_id=cost_metric.id,
                value=cost_value
            ))
        
        # Operating Expenses data (typically 10-15% of revenue)
        opex_metric = next((m for m in metrics if m.name == "operating_expenses"), None)
        for i, report in enumerate(reports):
            revenue_data = next((d for d in yearly_data if d.report_id == report.id and d.metric_id == revenue_metric.id), None)
            opex_ratio = random.uniform(0.10, 0.15)
            opex_value = revenue_data.value * opex_ratio
            yearly_data.append(YearlyData(
                report_id=report.id,
                metric_id=opex_metric.id,
                value=opex_value
            ))
        
        # Gross Profit Margin data (calculated from revenue and cost)
        gpm_metric = next((m for m in metrics if m.name == "gross_profit_margin"), None)
        for i, report in enumerate(reports):
            revenue_data = next((d for d in yearly_data if d.report_id == report.id and d.metric_id == revenue_metric.id), None)
            cost_data = next((d for d in yearly_data if d.report_id == report.id and d.metric_id == cost_metric.id), None)
            gross_profit = revenue_data.value - cost_data.value
            gpm_value = (gross_profit / revenue_data.value) * 100  # as percentage
            yearly_data.append(YearlyData(
                report_id=report.id,
                metric_id=gpm_metric.id,
                value=gpm_value
            ))
        
        # EPS data
        eps_metric = next((m for m in metrics if m.name == "eps"), None)
        base_eps = 4.25
        for i, report in enumerate(reports):
            # EPS follows similar pattern to revenue
            growth_rate = -0.18 if report.year == 2020 else random.uniform(0.05, 0.12)
            eps_value = base_eps * (1 + growth_rate) ** i
            yearly_data.append(YearlyData(
                report_id=report.id,
                metric_id=eps_metric.id,
                value=eps_value
            ))
        
        # NAV data
        nav_metric = next((m for m in metrics if m.name == "nav"), None)
        base_nav = 87.50
        for i, report in enumerate(reports):
            # NAV grows steadily except in 2020
            growth_rate = 0.02 if report.year == 2020 else random.uniform(0.04, 0.08)
            nav_value = base_nav * (1 + growth_rate) ** i
            yearly_data.append(YearlyData(
                report_id=report.id,
                metric_id=nav_metric.id,
                value=nav_value
            ))
        
        # Save yearly data
        db.bulk_add_and_commit(session, yearly_data)
        logger.info(f"Created {len(yearly_data)} yearly data points")
        
        # Create sample shareholders data
        shareholders_base = [
            {"name": "John Keells Holdings - Treasury", "percentage": 24.6},
            {"name": "Employees Provident Fund", "percentage": 12.3},
            {"name": "Sri Lanka Insurance Corporation Ltd", "percentage": 8.7},
            {"name": "Central Bank of Sri Lanka", "percentage": 6.2},
            {"name": "National Savings Bank", "percentage": 4.8},
            {"name": "Ceylon Investment PLC", "percentage": 3.9},
            {"name": "Bnymsanv Re-Emerging MKT Small", "percentage": 3.5},
            {"name": "Mellon Bank", "percentage": 3.2},
            {"name": "Northern Trust Company", "percentage": 2.8},
            {"name": "HSBC Intl Nominees Ltd", "percentage": 2.7},
            {"name": "Bank of Ceylon", "percentage": 2.5},
            {"name": "CITI Bank NY S/A Norges Bank", "percentage": 2.4},
            {"name": "Mercantile Investments PLC", "percentage": 2.1},
            {"name": "Deutsche Bank", "percentage": 1.9},
            {"name": "People's Bank", "percentage": 1.8},
            {"name": "Ceylon Guardian Investment", "percentage": 1.6},
            {"name": "Asian Alliance Insurance PLC", "percentage": 1.4},
            {"name": "Commercial Bank of Ceylon", "percentage": 1.3},
            {"name": "Softlogic Life Insurance PLC", "percentage": 1.2},
            {"name": "Mr. M.A. Yaseen", "percentage": 1.1}
        ]
        
        shareholders_data = []
        for report in reports:
            for rank, shareholder in enumerate(shareholders_base, 1):
                # Vary percentages slightly year to year
                variation = random.uniform(-0.5, 0.5)
                percentage = max(0.1, shareholder["percentage"] + variation)
                shares = int(percentage * 1315000000 / 100)  # Assuming 1.315B outstanding shares
                
                shareholders_data.append(ShareholderData(
                    report_id=report.id,
                    rank=rank,
                    shareholder_name=shareholder["name"],
                    ownership_percentage=percentage,
                    shares_count=shares
                ))
        
        # Save shareholders data
        db.bulk_add_and_commit(session, shareholders_data)
        logger.info(f"Created {len(shareholders_data)} shareholder data entries")
        
        logger.info("Sample data population completed successfully")
        
    except Exception as e:
        logger.error(f"Error populating sample data: {e}")
        if 'session' in locals():
            session.rollback()
        raise
    finally:
        if 'session' in locals():
            db.close_session(session)

if __name__ == "__main__":
    populate_sample_data() 