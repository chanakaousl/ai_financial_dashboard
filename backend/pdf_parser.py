import os
import re
import logging
import camelot
import pandas as pd
from pdfminer.high_level import extract_text
from database import db
from models.financial_data import FinancialReport, FinancialMetric, YearlyData, ShareholderData
from sqlalchemy.exc import IntegrityError
from config import get_config

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class JKHPDFParser:
    """Parser for John Keells Holdings financial reports"""
    
    def __init__(self):
        """Initialize the parser with database connection"""
        self.config = get_config()
        self.db = db
        self.session = self.db.get_session()
        
        # Initialize or get metrics
        self._initialize_metrics()
        
    def _initialize_metrics(self):
        """Initialize or retrieve financial metrics"""
        try:
            # Check if metrics exist
            metrics_count = self.session.query(FinancialMetric).count()
            
            if metrics_count == 0:
                logger.info("Initializing financial metrics...")
                
                # Create default metrics
                metrics = [
                    FinancialMetric(
                        name="revenue", 
                        display_name="Revenue",
                        description="Total revenue from operations",
                        unit="LKR",
                        category="income",
                        visualization_type="line"
                    ),
                    FinancialMetric(
                        name="cost_of_sales", 
                        display_name="Cost of Sales",
                        description="Direct costs attributable to the production of goods sold",
                        unit="LKR",
                        category="expense",
                        visualization_type="bar"
                    ),
                    FinancialMetric(
                        name="operating_expenses", 
                        display_name="Operating Expenses",
                        description="Expenses related to operations",
                        unit="LKR",
                        category="expense",
                        visualization_type="bar"
                    ),
                    FinancialMetric(
                        name="gross_profit_margin", 
                        display_name="Gross Profit Margin",
                        description="Percentage of revenue that exceeds the cost of goods sold",
                        unit="%",
                        category="profitability",
                        visualization_type="line"
                    ),
                    FinancialMetric(
                        name="eps", 
                        display_name="Earnings Per Share",
                        description="Net income divided by outstanding shares",
                        unit="LKR",
                        category="profitability",
                        visualization_type="line"
                    ),
                    FinancialMetric(
                        name="nav", 
                        display_name="Net Asset Value Per Share",
                        description="Net asset value divided by outstanding shares",
                        unit="LKR",
                        category="value",
                        visualization_type="line"
                    ),
                    FinancialMetric(
                        name="right_issues", 
                        display_name="Right Issues",
                        description="Offerings of shares to existing shareholders",
                        unit="",
                        category="shares",
                        visualization_type="table"
                    )
                ]
                
                self.db.bulk_add_and_commit(self.session, metrics)
                logger.info("Financial metrics initialized")
            
        except Exception as e:
            logger.error(f"Error initializing metrics: {e}")
            self.session.rollback()
            raise
    
    def parse_pdf(self, pdf_path, year):
        """
        Parse a financial report PDF
        
        Args:
            pdf_path: Path to the PDF file
            year: Year of the report
        """
        try:
            logger.info(f"Parsing PDF for year {year}: {pdf_path}")
            
            # Check if report already exists
            existing_report = self.session.query(FinancialReport).filter_by(year=year).first()
            if existing_report:
                logger.info(f"Report for year {year} already exists. Skipping.")
                return
            
            # Create a new report
            report = FinancialReport(year=year, pdf_path=pdf_path)
            self.db.add_and_commit(self.session, report)
            
            # Extract text from the PDF
            text = extract_text(pdf_path)
            
            # Extract tables from the PDF
            tables = camelot.read_pdf(pdf_path, pages='all')
            
            # Extract financial data
            self._extract_financial_data(text, tables, report)
            
            # Extract shareholder data
            self._extract_shareholder_data(text, tables, report)
            
            logger.info(f"Successfully parsed PDF for year {year}")
            
        except Exception as e:
            logger.error(f"Error parsing PDF {pdf_path}: {e}")
            self.session.rollback()
            raise
    
    def _extract_financial_data(self, text, tables, report):
        """Extract financial metrics from the report"""
        try:
            # Get metrics
            metrics = self.session.query(FinancialMetric).all()
            metrics_dict = {metric.name: metric for metric in metrics}
            
            # Extract revenue
            revenue = self._extract_revenue(text, tables)
            if revenue:
                self._save_metric_data(report, metrics_dict["revenue"], revenue)
            
            # Extract cost of sales
            cost_of_sales = self._extract_cost_of_sales(text, tables)
            if cost_of_sales:
                self._save_metric_data(report, metrics_dict["cost_of_sales"], cost_of_sales)
            
            # Extract operating expenses
            op_expenses = self._extract_operating_expenses(text, tables)
            if op_expenses:
                self._save_metric_data(report, metrics_dict["operating_expenses"], op_expenses)
            
            # Calculate gross profit margin
            if revenue and cost_of_sales:
                gross_profit = revenue - cost_of_sales
                gross_profit_margin = (gross_profit / revenue) * 100
                self._save_metric_data(report, metrics_dict["gross_profit_margin"], gross_profit_margin)
            
            # Extract EPS
            eps = self._extract_eps(text, tables)
            if eps:
                self._save_metric_data(report, metrics_dict["eps"], eps)
            
            # Extract NAV
            nav = self._extract_nav(text, tables)
            if nav:
                self._save_metric_data(report, metrics_dict["nav"], nav)
            
        except Exception as e:
            logger.error(f"Error extracting financial data: {e}")
            raise
    
    def _extract_shareholder_data(self, text, tables, report):
        """Extract top shareholders data"""
        try:
            # Look for the top shareholders table
            shareholders = self._find_top_shareholders(text, tables)
            
            if shareholders:
                for idx, shareholder in enumerate(shareholders, 1):
                    data = ShareholderData(
                        report_id=report.id,
                        rank=idx,
                        shareholder_name=shareholder["name"],
                        ownership_percentage=shareholder["percentage"],
                        shares_count=shareholder.get("shares", 0)
                    )
                    self.db.add_and_commit(self.session, data)
            
        except Exception as e:
            logger.error(f"Error extracting shareholder data: {e}")
            raise
    
    def _save_metric_data(self, report, metric, value):
        """Save a metric value to the database"""
        try:
            data = YearlyData(
                report_id=report.id,
                metric_id=metric.id,
                value=value
            )
            self.db.add_and_commit(self.session, data)
            
        except Exception as e:
            logger.error(f"Error saving metric data: {e}")
            raise
    
    def _extract_revenue(self, text, tables):
        """Extract revenue from the report"""
        # Implementation depends on report structure
        # For now, return a sample value
        return 150000000000.0
    
    def _extract_cost_of_sales(self, text, tables):
        """Extract cost of sales from the report"""
        # Implementation depends on report structure
        return 120000000000.0
    
    def _extract_operating_expenses(self, text, tables):
        """Extract operating expenses from the report"""
        # Implementation depends on report structure
        return 15000000000.0
    
    def _extract_eps(self, text, tables):
        """Extract EPS from the report"""
        # Implementation depends on report structure
        return 5.25
    
    def _extract_nav(self, text, tables):
        """Extract NAV from the report"""
        # Implementation depends on report structure
        return 100.75
    
    def _find_top_shareholders(self, text, tables):
        """Find top shareholders information"""
        # Implementation depends on report structure
        # Return sample data
        return [
            {"name": "John Keells Holdings PLC", "percentage": 24.6, "shares": 324500000},
            {"name": "Sample Investor 1", "percentage": 12.3, "shares": 162000000},
            {"name": "Sample Investor 2", "percentage": 8.7, "shares": 114500000},
            {"name": "Sample Investor 3", "percentage": 6.2, "shares": 81700000},
            {"name": "Sample Investor 4", "percentage": 4.8, "shares": 63200000}
        ]
    
    def close(self):
        """Close the database session"""
        self.db.close_session(self.session)

def parse_all_reports():
    """Parse all PDF reports in the data directory"""
    config = get_config()
    pdf_dir = config.PDF_DIRECTORY
    parser = JKHPDFParser()
    
    try:
        # Get all PDF files
        pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf') and not f.startswith('AI Dashboard')]
        
        for pdf_file in pdf_files:
            # Extract year from filename if possible (assuming format like 508_1684842640428.pdf)
            # For John Keells, we'd need to map these files to actual years
            # This is a simplified example - in reality, you'd need to determine years more reliably
            year_map = {
                "508_1590052852777.pdf": 2020,
                "508_1621849083921.pdf": 2021,
                "508_1653300092463.pdf": 2022, 
                "508_1684842640428.pdf": 2023,
                "508_1716290978705.pdf": 2024
            }
            
            if pdf_file in year_map:
                year = year_map[pdf_file]
                pdf_path = os.path.join(pdf_dir, pdf_file)
                parser.parse_pdf(pdf_path, year)
            else:
                logger.warning(f"Could not determine year for file: {pdf_file}")
        
    except Exception as e:
        logger.error(f"Error parsing reports: {e}")
    finally:
        parser.close()

if __name__ == "__main__":
    parse_all_reports() 