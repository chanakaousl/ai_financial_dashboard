"""
Utility for extracting financial data from PDF reports.
This script handles:
1. Reading the PDF files
2. Extracting the year
3. Identifying and extracting key tables
4. Processing and structuring the data
"""
import os
import re
import logging
import camelot
import pandas as pd
from pdfminer.high_level import extract_text
from ..database import db
from ..models.financial_data import FinancialReport, FinancialMetric, YearlyData

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFExtractor:
    """
    Class for extracting structured financial data from PDF reports.
    """
    
    def __init__(self, pdf_directory, flavor='lattice', focus_metrics=None):
        """
        Initialize the PDF extractor.
        
        Args:
            pdf_directory (str): Directory containing PDF files
            flavor (str, optional): The table extraction method to use ('lattice' or 'stream'). 
                                   Use 'stream' to avoid Ghostscript dependency. Defaults to 'lattice'.
            focus_metrics (list, optional): List of specific metric names to focus on. 
                                          If provided, only these metrics will be extracted.
        """
        self.pdf_directory = pdf_directory
        self.parser = PDFParser(pdf_directory, flavor=flavor)
        self.focus_metrics = focus_metrics
        
        # Define simplified mapping for core metrics
        self.core_metric_keywords = {
            'revenue': ['revenue', 'total revenue', 'group revenue', 'income'],
            'cost_of_sales': ['cost of sales', 'cost of goods sold', 'cost of revenue'],
            'operating_expenses': ['operating expenses', 'operating costs', 'administrative expenses', 
                                 'selling and distribution expenses', 'distribution expenses'],
            'eps': ['eps', 'earnings per share', 'basic earnings per share', 'diluted earnings per share'],
            'net_asset_per_share': ['net asset per share', 'nav per share', 'net assets per share'],
            'right_issues': ['right issue', 'rights issue', 'right issues'],
            'top_20_shareholders': ['top shareholders', 'top 20 shareholders', 'major shareholders']
        }
        
        # If focus metrics are provided, filter the keywords map
        if self.focus_metrics:
            self.known_metrics = {k: v for k, v in self.core_metric_keywords.items() if k in self.focus_metrics}
        else:
            self.known_metrics = self.core_metric_keywords
    
    def process_all_reports(self):
        """
        Process all PDF reports in the directory and store data in the database.
        
        Returns:
            dict: Summary of the processing results
        """
        pdf_files = self.parser.list_pdf_files()
        results = {
            'total_files': len(pdf_files),
            'processed_files': 0,
            'failed_files': 0,
            'extracted_metrics': 0
        }
        
        # Process each file
        for pdf_path in pdf_files:
            # Skip the requirements document
            if 'AI Dashboard for John Keells Financial Data.pdf' in pdf_path:
                continue
                
            try:
                # Extract year from filename or content
                year = self._extract_year_from_file(pdf_path)
                
                if not year:
                    logger.warning(f"Could not determine year for {pdf_path}")
                    results['failed_files'] += 1
                    continue
                
                # Check if report already exists
                session = db.get_session()
                existing_report = session.query(FinancialReport).filter_by(year=year).first()
                
                if existing_report:
                    logger.info(f"Report for year {year} already exists in database")
                    db.close_session(session)
                    continue
                
                # Create new report entry
                filename = os.path.basename(pdf_path)
                title = f"Annual Report {year}"
                report = FinancialReport(
                    year=year,
                    title=title,
                    file_path=pdf_path
                )
                
                db.add_and_commit(session, report)
                logger.info(f"Added report for year {year} to database")
                
                # Extract and store financial metrics
                metrics_count = self._extract_and_store_metrics(pdf_path, report.id, session)
                
                # Extract and store top shareholders if available and in focus metrics
                if not self.focus_metrics or 'top_20_shareholders' in self.focus_metrics:
                    shareholders_count = self._extract_and_store_shareholders(pdf_path, report.id, session)
                    metrics_count += shareholders_count
                
                # Extract and store right issues if available and in focus metrics
                if not self.focus_metrics or 'right_issues' in self.focus_metrics:
                    rights_count = self._extract_and_store_right_issues(pdf_path, report.id, session)
                    metrics_count += rights_count
                
                # Calculate and store gross profit margin if we have revenue and cost_of_sales
                if not self.focus_metrics or ('gross_profit_margin' in self.focus_metrics and 
                                           'revenue' in self.focus_metrics and 
                                           'cost_of_sales' in self.focus_metrics):
                    derived_count = self._calculate_and_store_gross_profit_margin(report.id, session)
                    metrics_count += derived_count
                
                results['extracted_metrics'] += metrics_count
                results['processed_files'] += 1
                db.close_session(session)
                
            except Exception as e:
                logger.error(f"Error processing {pdf_path}: {e}")
                results['failed_files'] += 1
        
        return results
    
    def _extract_year_from_file(self, pdf_path):
        """
        Extract the year from the PDF file using filename or content.
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            int: The year, or None if not found
        """
        # Try to extract from filename first
        filename = os.path.basename(pdf_path)
        year_match = re.search(r'20\d{2}', filename)
        
        if year_match:
            return int(year_match.group(0))
        
        # Extract from content
        try:
            text = self.parser.extract_text(pdf_path, end_page=10)  # Only search first 10 pages
            
            # Look for annual report year pattern
            year_patterns = [
                r'Annual Report (\d{4})',
                r'Annual Report (\d{4})/(\d{4})',
                r'Annual Report (\d{4})-(\d{2})',
                r'Financial Year (\d{4})'
            ]
            
            for pattern in year_patterns:
                matches = re.findall(pattern, text)
                if matches:
                    if isinstance(matches[0], tuple):
                        return int(matches[0][0])  # Take the first year in case of ranges
                    else:
                        return int(matches[0])
            
            # If we can't find specific patterns, look for any 4-digit year
            # Prioritize years that are likely to be annual report years (2017-2024)
            years = re.findall(r'\b(20\d{2})\b', text)
            valid_years = [int(y) for y in years if 2017 <= int(y) <= 2024]
            
            if valid_years:
                # Count occurrences of each year and take the most frequent
                year_counts = {}
                for year in valid_years:
                    year_counts[year] = year_counts.get(year, 0) + 1
                
                return max(year_counts.items(), key=lambda x: x[1])[0]
        
        except Exception as e:
            logger.error(f"Error extracting year from PDF content: {e}")
        
        return None
    
    def _extract_and_store_metrics(self, pdf_path, report_id, session):
        """
        Extract financial metrics from the PDF and store them in the database.
        
        Args:
            pdf_path (str): Path to the PDF file
            report_id (int): ID of the report in the database
            session: Database session
            
        Returns:
            int: Number of metrics extracted and stored
        """
        metrics_count = 0
        
        try:
            # Extract tables from the PDF
            tables = self.parser.extract_tables(pdf_path)
            
            # Process each table to identify financial metrics
            for table_df in tables:
                metrics_in_table = self._identify_metrics_in_table(table_df)
                
                for metric_name, value in metrics_in_table.items():
                    # Check if metric exists in database
                    metric = session.query(FinancialMetric).filter_by(name=metric_name).first()
                    
                    if not metric:
                        continue  # Skip metrics that are not in our predefined core metrics
                    
                    # Create yearly data entry
                    yearly_data = YearlyData(
                        report_id=report_id,
                        metric_id=metric.id,
                        value=value,
                        notes=f"Extracted from {os.path.basename(pdf_path)}"
                    )
                    
                    db.add_and_commit(session, yearly_data)
                    metrics_count += 1
                    logger.info(f"Added {metric_name} = {value} for report {report_id}")
            
            # If tables didn't yield enough metrics, try text-based extraction
            if metrics_count < 5:
                text_metrics = self._extract_metrics_from_text(pdf_path)
                
                for metric_name, value in text_metrics.items():
                    # Skip if we already have this metric
                    existing_data = session.query(YearlyData).join(FinancialMetric).filter(
                        FinancialMetric.name == metric_name,
                        YearlyData.report_id == report_id
                    ).first()
                    
                    if existing_data:
                        continue
                    
                    # Check if metric exists in database
                    metric = session.query(FinancialMetric).filter_by(name=metric_name).first()
                    
                    if not metric:
                        continue  # Skip metrics that are not in our predefined core metrics
                    
                    # Create yearly data entry
                    yearly_data = YearlyData(
                        report_id=report_id,
                        metric_id=metric.id,
                        value=value,
                        notes=f"Extracted from text in {os.path.basename(pdf_path)}"
                    )
                    
                    db.add_and_commit(session, yearly_data)
                    metrics_count += 1
                    logger.info(f"Added {metric_name} = {value} for report {report_id} (from text)")
            
            return metrics_count
            
        except Exception as e:
            logger.error(f"Error extracting metrics from {pdf_path}: {e}")
            return metrics_count
    
    def _extract_and_store_shareholders(self, pdf_path, report_id, session):
        """
        Extract top shareholders from the PDF and store them in the database.
        
        Args:
            pdf_path (str): Path to the PDF file
            report_id (int): ID of the report in the database
            session: Database session
            
        Returns:
            int: Number of shareholder entries extracted
        """
        count = 0
        
        try:
            # Find the section with top shareholders - typically labeled as "Top 20 Shareholders"
            text = self.parser.extract_text(pdf_path)
            
            # Look for shareholders table section
            shareholders_section = None
            section_patterns = [
                r'(?:Top|Major|Principal)\s+(?:20|Twenty)?\s+Shareholders.*?(?=\n\n\n)',
                r'Share\s+Information.*?Shareholders.*?(?=\n\n\n)',
                r'Shareholder\s+Information.*?(?=\n\n\n)'
            ]
            
            for pattern in section_patterns:
                match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
                if match:
                    shareholders_section = match.group(0)
                    break
            
            if not shareholders_section:
                logger.info(f"No shareholders section found in {pdf_path}")
                return 0
            
            # Try to extract shareholders from tables
            tables = self.parser.extract_tables(pdf_path)
            for table_df in tables:
                # Check if this looks like a shareholders table
                table_str = table_df.to_string().lower()
                if any(keyword in table_str for keyword in ['shareholder', 'name', 'holding', 'ownership', 'percentage']):
                    # This might be a shareholders table
                    # Store this as a single metric with notes containing the shareholder data
                    shareholders_data = table_df.to_json(orient='records')
                    
                    # Check if metric exists
                    metric = session.query(FinancialMetric).filter_by(name='top_20_shareholders').first()
                    
                    if not metric:
                        continue  # Skip if not in our predefined core metrics
                    
                    # Create yearly data entry with JSON data in notes
                    yearly_data = YearlyData(
                        report_id=report_id,
                        metric_id=metric.id,
                        value=0,  # No numeric value, data is in notes
                        notes=shareholders_data
                    )
                    
                    db.add_and_commit(session, yearly_data)
                    count += 1
                    logger.info(f"Added shareholders data for report {report_id}")
                    break
            
            return count
            
        except Exception as e:
            logger.error(f"Error extracting shareholders from {pdf_path}: {e}")
            return 0
    
    def _extract_and_store_right_issues(self, pdf_path, report_id, session):
        """
        Extract right issues information from the PDF and store it in the database.
        
        Args:
            pdf_path (str): Path to the PDF file
            report_id (int): ID of the report in the database
            session: Database session
            
        Returns:
            int: Number of right issues entries extracted
        """
        count = 0
        
        try:
            # Look for right issues in the text
            text = self.parser.extract_text(pdf_path)
            
            # Look for right issues patterns
            right_issues_patterns = [
                r'rights?\s+issues?\s+(?:of|:)?\s*(?:Rs\.?|LKR)?\s*([\d,]+(?:\.\d+)?)',
                r'rights?\s+issues?\s+at\s+(?:Rs\.?|LKR)?\s*([\d,]+(?:\.\d+)?)',
                r'rights?\s+issues?\s+ratio\s*(?:of|:)?\s*([\d,]+(?:\.\d+)?)'
            ]
            
            for pattern in right_issues_patterns:
                matches = re.findall(pattern, text.lower())
                if matches:
                    # Found right issues information
                    # Check if metric exists
                    metric = session.query(FinancialMetric).filter_by(name='right_issues').first()
                    
                    if not metric:
                        continue  # Skip if not in our predefined core metrics
                    
                    # Extract value from the first match
                    try:
                        value = float(matches[0].replace(',', ''))
                    except (ValueError, IndexError):
                        value = 0
                    
                    # Create yearly data entry
                    yearly_data = YearlyData(
                        report_id=report_id,
                        metric_id=metric.id,
                        value=value,
                        notes=f"Right issues information extracted from {os.path.basename(pdf_path)}"
                    )
                    
                    db.add_and_commit(session, yearly_data)
                    count += 1
                    logger.info(f"Added right issues data for report {report_id}: {value}")
                    break
            
            return count
            
        except Exception as e:
            logger.error(f"Error extracting right issues from {pdf_path}: {e}")
            return 0
    
    def _calculate_and_store_gross_profit_margin(self, report_id, session):
        """
        Calculate and store gross profit margin using revenue and cost of sales.
        
        Args:
            report_id (int): ID of the report in the database
            session: Database session
            
        Returns:
            int: 1 if calculated and stored, 0 otherwise
        """
        try:
            # Get revenue
            revenue_metric = session.query(FinancialMetric).filter_by(name='revenue').first()
            if not revenue_metric:
                return 0
                
            revenue_data = session.query(YearlyData).filter(
                YearlyData.report_id == report_id,
                YearlyData.metric_id == revenue_metric.id
            ).first()
            
            if not revenue_data or revenue_data.value <= 0:
                return 0
                
            revenue = revenue_data.value
            
            # Get cost of sales
            cost_metric = session.query(FinancialMetric).filter_by(name='cost_of_sales').first()
            if not cost_metric:
                return 0
                
            cost_data = session.query(YearlyData).filter(
                YearlyData.report_id == report_id,
                YearlyData.metric_id == cost_metric.id
            ).first()
            
            if not cost_data:
                return 0
                
            cost = cost_data.value
            
            # Calculate gross profit margin
            gross_profit = revenue - cost
            gross_profit_margin = (gross_profit / revenue) * 100
            
            # Get the gross profit margin metric
            margin_metric = session.query(FinancialMetric).filter_by(name='gross_profit_margin').first()
            if not margin_metric:
                return 0
            
            # Create yearly data entry
            yearly_data = YearlyData(
                report_id=report_id,
                metric_id=margin_metric.id,
                value=gross_profit_margin,
                notes=f"Calculated as ((revenue - cost_of_sales) / revenue) * 100"
            )
            
            db.add_and_commit(session, yearly_data)
            logger.info(f"Calculated gross profit margin for report {report_id}: {gross_profit_margin:.2f}%")
            return 1
            
        except Exception as e:
            logger.error(f"Error calculating gross profit margin for report {report_id}: {e}")
            return 0
    
    def _identify_metrics_in_table(self, table_df):
        """
        Identify financial metrics in a table.
        
        Args:
            table_df (DataFrame): Pandas DataFrame containing table data
            
        Returns:
            dict: Dictionary of metric names and values
        """
        metrics = {}
        
        # Convert table to string for easier searching
        table_str = table_df.to_string().lower()
        
        # Check each known metric
        for category, keywords in self.known_metrics.items():
            for keyword in keywords:
                if keyword in table_str:
                    # Find the row containing the keyword
                    for i, row in table_df.iterrows():
                        row_str = ' '.join(str(cell).lower() for cell in row).strip()
                        if keyword in row_str:
                            # Try to extract the value
                            value = self._extract_numeric_value(row)
                            if value is not None:
                                metrics[category] = value
                                break
        
        return metrics
    
    def _extract_numeric_value(self, row):
        """
        Extract a numeric value from a table row.
        
        Args:
            row: Pandas Series representing a row in a table
            
        Returns:
            float: Extracted numeric value, or None if not found
        """
        # Convert row to string values
        row_vals = [str(val).strip() for val in row]
        
        # Look for numeric values
        for val in row_vals:
            # Remove common non-numeric characters
            clean_val = re.sub(r'[^\d.-]', '', val)
            try:
                if clean_val:
                    return float(clean_val)
            except ValueError:
                pass
        
        return None
    
    def _extract_metrics_from_text(self, pdf_path):
        """
        Extract financial metrics from the PDF text content.
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            dict: Dictionary of metric names and values
        """
        metrics = {}
        text = self.parser.extract_text(pdf_path)
        
        # Define patterns for core metrics
        patterns = {
            # Revenue patterns
            'revenue': [
                r'(?:total|group)?\s*revenue\s*(?:of|:)?\s*(?:Rs\.?|LKR)?\s*([\d,]+(?:\.\d+)?)',
                r'revenue\s*(?:for the (?:year|period))?\s*(?:of|:)?\s*(?:Rs\.?|LKR)?\s*([\d,]+(?:\.\d+)?)',
                r'total\s*income\s*(?:of|:)?\s*(?:Rs\.?|LKR)?\s*([\d,]+(?:\.\d+)?)'
            ],
            
            # Cost of sales patterns
            'cost_of_sales': [
                r'cost\s*of\s*sales\s*(?:of|:)?\s*(?:Rs\.?|LKR)?\s*([\d,]+(?:\.\d+)?)',
                r'cost\s*of\s*goods\s*sold\s*(?:of|:)?\s*(?:Rs\.?|LKR)?\s*([\d,]+(?:\.\d+)?)'
            ],
            
            # Operating expenses patterns
            'operating_expenses': [
                r'(?:total)?\s*operating\s*expenses\s*(?:of|:)?\s*(?:Rs\.?|LKR)?\s*([\d,]+(?:\.\d+)?)',
                r'administrative\s*expenses\s*(?:of|:)?\s*(?:Rs\.?|LKR)?\s*([\d,]+(?:\.\d+)?)',
                r'selling\s*and\s*distribution\s*expenses\s*(?:of|:)?\s*(?:Rs\.?|LKR)?\s*([\d,]+(?:\.\d+)?)'
            ],
            
            # EPS patterns
            'eps': [
                r'(?:basic)?\s*earnings\s*per\s*share\s*(?:of|:)?\s*(?:Rs\.?|LKR)?\s*([\d,]+(?:\.\d+)?)',
                r'eps\s*(?:of|:)?\s*(?:Rs\.?|LKR)?\s*([\d,]+(?:\.\d+)?)',
                r'diluted\s*earnings\s*per\s*share\s*(?:of|:)?\s*(?:Rs\.?|LKR)?\s*([\d,]+(?:\.\d+)?)'
            ],
            
            # Net asset per share patterns
            'net_asset_per_share': [
                r'net\s*assets?\s*per\s*share\s*(?:of|:)?\s*(?:Rs\.?|LKR)?\s*([\d,]+(?:\.\d+)?)',
                r'nav\s*per\s*share\s*(?:of|:)?\s*(?:Rs\.?|LKR)?\s*([\d,]+(?:\.\d+)?)'
            ]
        }
        
        # Filter patterns if we have focus metrics
        if self.focus_metrics:
            patterns = {k: v for k, v in patterns.items() if k in self.focus_metrics}
        
        # Process each metric with its patterns
        for metric_name, pattern_list in patterns.items():
            values = []
            
            for pattern in pattern_list:
                matches = re.findall(pattern, text.lower())
                for match in matches:
                    try:
                        values.append(float(match.replace(',', '')))
                    except ValueError:
                        continue
            
            if values:
                # Use the highest value found as this is often the total
                metrics[metric_name] = max(values)  
                logger.info(f"Extracted {metric_name}: {metrics[metric_name]}")
        
        # Right issues processing (if in focus metrics)
        if not self.focus_metrics or 'right_issues' in self.focus_metrics:
            right_issues_patterns = [
                r'rights?\s+issues?\s+(?:of|:)?\s*(?:Rs\.?|LKR)?\s*([\d,]+(?:\.\d+)?)',
                r'rights?\s+issues?\s+at\s+(?:Rs\.?|LKR)?\s*([\d,]+(?:\.\d+)?)',
                r'rights?\s+issues?\s+ratio\s*(?:of|:)?\s*([\d,]+(?:\.\d+)?)'
            ]
            
            for pattern in right_issues_patterns:
                matches = re.findall(pattern, text.lower())
                if matches:
                    try:
                        metrics['right_issues'] = float(matches[0].replace(',', ''))
                        logger.info(f"Extracted right issues: {metrics['right_issues']}")
                        break
                    except (ValueError, IndexError):
                        pass
        
        return metrics

# Import the PDF parser to use in the extractor
from .pdf_parser import PDFParser 