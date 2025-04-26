#!/usr/bin/env python
"""
Financial Data Extractor

A single, focused script to extract financial metrics from PDF annual reports.
extracting only the core financial metrics needed for the dashboard.

Usage:
    python -m backend.scripts.financial_data_extractor
"""
import os
import sys
import logging
import re
from pathlib import Path
import camelot
from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.config import get_config
from backend.database import db
from backend.models.financial_data import FinancialReport, FinancialMetric, YearlyData, ShareholderData

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FinancialDataExtractor:
    """
    Class for extracting core financial metrics from PDF annual reports.
    Uses a dynamic approach without relying on specific page numbers.
    """
    
    def __init__(self, pdf_directory):
        """Initialize the extractor with PDF directory."""
        self.pdf_directory = pdf_directory
        
        # Define the core metrics we need to extract
        self.core_metrics = [
            {"name": "revenue", "description": "Total Revenue from annual report", "unit": "LKR", "category": "revenue"},
            {"name": "cost_of_sales", "description": "Cost of Sales from annual report", "unit": "LKR", "category": "cost_of_sales"},
            {"name": "operating_expenses", "description": "Operating Expenses from annual report", "unit": "LKR", "category": "operating_expenses"},
            {"name": "gross_profit_margin", "description": "Gross Profit Margin (Revenue - Cost) / Revenue", "unit": "%", "category": "gross_profit_margin"},
            {"name": "eps", "description": "Earnings Per Share from annual report", "unit": "LKR/share", "category": "eps"},
            {"name": "net_asset_per_share", "description": "Net Asset Per Share from annual report", "unit": "LKR/share", "category": "net_asset_per_share"},
            {"name": "right_issues", "description": "Right Issues information", "unit": "LKR", "category": "right_issues"},
            {"name": "top_20_shareholders", "description": "Top 20 Shareholders information", "unit": "", "category": "shareholders"}
        ]
        
        # Define keywords to identify each metric in the PDF text and tables
        self.metric_keywords = {
            "revenue": ["revenue", "total revenue", "group revenue", "consolidated revenue"],
            "cost_of_sales": ["cost of sales", "cost of goods sold"],
            "operating_expenses": ["operating expenses", "operating costs", "administrative expenses", "selling and distribution expenses"],
            "eps": ["earnings per share", "eps", "basic earnings per share", "diluted earnings per share"],
            "net_asset_per_share": ["net asset per share", "nav per share", "net assets per share", "net asset value per share"],
            "right_issues": ["right issue", "rights issue", "right issues", "rights offering"],
            "top_20_shareholders": ["top 20 shareholders", "top twenty shareholders", "shareholder information", "major shareholders"]
        }
        
        # Improved regex patterns for extracting values
        self.metric_patterns = {
            "revenue": r'(?i)(revenue|income|turnover)[^a-zA-Z0-9]*([\d,]+(?:\.\d+)?)',
            "cost_of_sales": r'(?i)cost\s+of\s+sales[^a-zA-Z0-9]*([\d,]+(?:\.\d+)?)',
            "operating_expenses": r'(?i)(administrative|selling\s+and\s+distribution|other\s+operating)\s+expenses[^a-zA-Z0-9]*([\d,]+(?:\.\d+)?)',
            "gross_profit_margin": r'(?i)gross\s+profit(?:\s+margin)?[^a-zA-Z0-9]*([\d,]+(?:\.\d+)?%?)',
            "eps": r'(?i)(basic|diluted)\s+earnings\s+per\s+share[^a-zA-Z0-9]*([\d\.]+)',
            "net_asset_per_share": r'(?i)net\s+assets?\s+(?:value\s+)?per\s+(?:ordinary\s+)?share[^a-zA-Z0-9]*([\d\.,]+)',
            "right_issues": r'(?i)(right\s+issue|rights\s+issue|rights\s+offering|issuance\s+of\s+rights|entitlement\s+offer)[^a-zA-Z0-9]*([\d,]+(?:\.\d+)?)',
            "shareholder_row": r'(?P<rank>\d+)[.\s]+(?P<name>.*?)\s+(?P<shares>[\d,]+)\s+(?P<percent>[\d\.]+)%?'
        }
        
        # Components of operating expenses
        self.expense_components = [
            "selling and distribution expenses", 
            "administrative expenses", 
            "administration expenses",
            "other operating expenses"
        ]
    
    def process_all_reports(self):
        """
        Process all PDF reports in the directory and store data in the database.
        
        Returns:
            dict: Summary of the processing results
        """
        results = {
            'total_files': 0,
            'processed_files': 0,
            'failed_files': 0,
            'extracted_metrics': 0
        }
        
        # Clean the database first
        self._clean_database()
        
        # Setup core metrics
        session = db.get_session()
        self._setup_core_metrics(session)
        db.close_session(session)
        
        # Get all PDF files
        pdf_files = []
        for file in os.listdir(self.pdf_directory):
            if file.lower().endswith('.pdf') and 'AI Dashboard for John Keells Financial Data' not in file:
                pdf_files.append(os.path.join(self.pdf_directory, file))
        
        results['total_files'] = len(pdf_files)
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        # Process each file
        for pdf_path in pdf_files:
            try:
                logger.info(f"Processing file: {os.path.basename(pdf_path)}")
                
                # Extract year from filename or content
                year = self._extract_year_from_file(pdf_path)
                
                if not year:
                    logger.warning(f"Could not determine year for {pdf_path}")
                    results['failed_files'] += 1
                    continue
                
                # Create a new report entry
                session = db.get_session()
                filename = os.path.basename(pdf_path)
                title = f"Annual Report {year}"
                
                # Check if the report for this year already exists
                existing_report = session.query(FinancialReport).filter(
                    FinancialReport.year == year
                ).first()
                
                if existing_report:
                    report = existing_report
                    logger.info(f"Found existing report for year {year}")
                else:
                    report = FinancialReport(
                        year=year,
                        title=title,
                        file_path=pdf_path
                    )
                    db.add_and_commit(session, report)
                    logger.info(f"Added report for year {year} to database")
                
                # Extract metrics from the report
                metrics_count = self._extract_metrics_from_report(pdf_path, report.id, session)
                
                results['extracted_metrics'] += metrics_count
                results['processed_files'] += 1
                db.close_session(session)
                
            except Exception as e:
                logger.error(f"Error processing {pdf_path}: {e}")
                results['failed_files'] += 1
        
        # Report results
        logger.info(f"Extraction completed. Results: {results}")
        return results
    
    def _clean_database(self):
        """Delete all existing data from the database."""
        logger.info("Cleaning database...")
        session = db.get_session()
        
        try:
            # Delete all shareholder data entries first (due to foreign key constraints)
            shareholder_data_count = session.query(ShareholderData).delete()
            logger.info(f"Deleted {shareholder_data_count} entries from ShareholderData table")

            # Delete all yearly data entries
            yearly_data_count = session.query(YearlyData).delete()
            logger.info(f"Deleted {yearly_data_count} entries from YearlyData table")
            
            # Delete all financial reports
            reports_count = session.query(FinancialReport).delete()
            logger.info(f"Deleted {reports_count} entries from FinancialReport table")
            
            # Delete all financial metrics
            metrics_count = session.query(FinancialMetric).delete()
            logger.info(f"Deleted {metrics_count} entries from FinancialMetric table")
            
            # Commit the changes
            session.commit()
            logger.info("Database cleanup completed successfully")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error during database cleanup: {e}")
        finally:
            db.close_session(session)
    
    def _setup_core_metrics(self, session):
        """Set up the core metrics in the database."""
        logger.info("Setting up core metrics...")
        
        # Add each core metric
        for metric_info in self.core_metrics:
            metric = FinancialMetric(
                name=metric_info["name"],
                description=metric_info["description"],
                unit=metric_info["unit"],
                category=metric_info["category"]
            )
            session.add(metric)
            logger.info(f"Created metric: {metric_info['name']}")
        
        # Commit all metrics at once
        session.commit()
        logger.info("Core metrics setup completed successfully")
    
    def _extract_year_from_file(self, pdf_path):
        """Extract the year from the PDF file using filename or content."""
        # Try to extract from filename first
        filename = os.path.basename(pdf_path)
        year_match = re.search(r'20\d{2}', filename)
        
        if year_match:
            return int(year_match.group(0))
        
        # Extract from content
        try:
            # Only read the first few pages to find the year
            text = extract_text(pdf_path, page_numbers=list(range(5)))
            
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
    
    def _extract_metrics_from_report(self, pdf_path, report_id, session):
        """Extract all core metrics from a report."""
        metrics_count = 0
        metrics_db = {}
        
        # Get all metric definitions from the database
        for metric in session.query(FinancialMetric).all():
            metrics_db[metric.name] = metric
        
        # Get the report year for context
        report_year = None
        filename = os.path.basename(pdf_path)
        year_match = re.search(r'20(\d{2})', filename)
        if year_match:
            report_year = int("20" + year_match.group(1))
        
        # Number of pages in the PDF
        try:
            num_pages = self._get_page_count(pdf_path)
            logger.info(f"PDF has {num_pages} pages")
        except Exception as e:
            logger.error(f"Error getting page count: {e}")
            num_pages = 100  # Default to a reasonable number
        
        # Important pages to check - page ranges based on typical annual report structure
        important_ranges = {
            'highlights': list(range(15, 26)),  # Performance highlights, typically early in report
            'financial_statements': list(range(170, 201)),  # Income statement, balance sheet
            'financial_review': list(range(35, 45)),  # Management discussion & analysis
            'shareholder_info': list(range(280, num_pages))  # Shareholder information typically at end
        }
        
        # Identify key pages by searching for specific sections
        key_pages = self._identify_key_pages(pdf_path, num_pages)
        
        # Log the key pages found
        logger.info(f"Identified key pages: {key_pages}")
        
        # For each metric, try to extract from the most relevant pages first
        for metric_name in ["revenue", "cost_of_sales", "operating_expenses", "eps", 
                          "net_asset_per_share", "right_issues", "top_20_shareholders"]:
            
            if metric_name not in metrics_db:
                logger.warning(f"Metric {metric_name} not found in database")
                continue
                
            # Skip if we already have this metric
            if self._check_if_metric_exists(session, report_id, metrics_db[metric_name].id):
                logger.info(f"Skipping {metric_name} for report {report_id} (already exists in DB)")
                continue
            
            # Determine the best pages to look based on the metric
            search_pages = []
            
            # Instead of hardcoding specific sections, search more pages for important metrics
            if metric_name == "net_asset_per_share":
                # Search many pages throughout the document to ensure we find this critical metric
                # Sample pages across the entire document, focusing more on financial sections
                step = max(1, num_pages // 20)  # Sample roughly 20 pages
                search_pages.extend(range(0, min(num_pages, 500), step))
                
                # Add all key financial pages we've identified
                for section, page in key_pages.items():
                    search_pages.append(page)
                    search_pages.append(page + 1)  # Also check next page
                
                # Add ranges that typically contain financial data
                for pages in important_ranges.values():
                    search_pages.extend(pages)
            elif metric_name in ["revenue", "cost_of_sales", "eps"]:
                if 'income_statement' in key_pages:
                    search_pages.extend([key_pages['income_statement'], key_pages['income_statement'] + 1])
                if 'highlights' in key_pages:
                    search_pages.append(key_pages['highlights'])
                search_pages.extend(important_ranges['financial_statements'])
                # Add extra pages for metrics that might be in the notes section
                search_pages.extend(range(200, 250))
            elif metric_name == "operating_expenses":
                if 'income_statement' in key_pages:
                    search_pages.extend([key_pages['income_statement'], key_pages['income_statement'] + 1])
                search_pages.extend(important_ranges['financial_statements'])
                search_pages.extend(important_ranges['financial_review'])
            elif metric_name == "right_issues":
                # Search financial statements, equity statement, and potentially notes sections
                if 'equity_statement' in key_pages:
                    search_pages.append(key_pages['equity_statement'])
                search_pages.extend(important_ranges['financial_statements'])
                search_pages.extend(range(200, 250)) # Add typical notes pages
            elif metric_name == "top_20_shareholders":
                if 'shareholder_info' in key_pages:
                    search_pages.append(key_pages['shareholder_info'])
                search_pages.extend(important_ranges['shareholder_info'])
            
            # Remove duplicates and sort
            search_pages = sorted(list(set([p for p in search_pages if p < num_pages])))
            
            logger.info(f"Extracting {metric_name} from {os.path.basename(pdf_path)} on pages: {search_pages}")
            
            value = None
            
            # Special handling for operating expenses which requires extracting components
            if metric_name == "operating_expenses":
                value = self._extract_operating_expenses(pdf_path, search_pages)
            # Special handling for EPS with more specific patterns
            elif metric_name == "eps":
                value = self._extract_eps(pdf_path, search_pages)
            elif metric_name == "net_asset_per_share":
                value = self._extract_net_asset_per_share(pdf_path, search_pages)
                
                # If no value found using the specialized method, try generic extraction across all pages
                if value is None:
                    logger.warning("Specialized extraction failed for net_asset_per_share. Trying generic approach...")
                    # Try with a simpler approach
                    value = self._extract_net_asset_simple(pdf_path, search_pages)
            # Special handling for top 20 shareholders which needs table extraction and saving to separate table
            elif metric_name == "top_20_shareholders":
                # This metric is handled differently - extract and save directly to ShareholderData table
                shareholder_count = self._extract_and_save_shareholders_info(session, report_id, pdf_path, search_pages)
                if shareholder_count > 0:
                    metrics_count += 1 # Count as one 'metric' extracted for reporting purposes
                continue # Skip the generic value saving logic below for shareholders
            elif metric_name == "right_issues":
                 # This metric is handled differently - extract details and save to notes
                extracted_notes = self._extract_and_save_right_issues_info(session, report_id, metrics_db[metric_name].id, pdf_path, search_pages)
                if extracted_notes: # If we found *any* info, count it
                     metrics_count += 1
                continue # Skip the generic value saving logic below for this metric
            else:
                # First try extracting from tables
                value = self._extract_from_tables(pdf_path, search_pages, metric_name)
                
                # If no value found in tables, try extracting from text
                if value is None:
                    for page in search_pages:
                        value = self._extract_metric_from_page(pdf_path, page, metric_name)
                        if value is not None:
                            break
            
            # Fallback logic removed for right_issues as it's handled above

            # Save the extracted value for metrics other than shareholders and right issues
            if value is not None:
                 # Ensure we don't try to save shareholders or right issues here again
                if metric_name not in ["top_20_shareholders", "right_issues"]:
                    self._save_metric(session, report_id, metrics_db[metric_name].id, value, pdf_path)
                    metrics_count += 1
                    logger.info(f"Extracted {metric_name} with value {value}")
            elif metric_name not in ["top_20_shareholders", "right_issues"]: # Don't warn for these handled metrics
                logger.warning(f"Could not extract {metric_name}")
                
        # Calculate gross profit margin
        if "gross_profit_margin" in metrics_db and not self._check_if_metric_exists(session, report_id, metrics_db["gross_profit_margin"].id):
            success = self._calculate_gross_profit_margin(session, report_id, metrics_db)
            if success:
                metrics_count += 1
                logger.info("Calculated gross profit margin")
        
        return metrics_count
    
    def _identify_key_pages(self, pdf_path, num_pages):
        """Identify key pages in the report like income statement, balance sheet, etc."""
        key_pages = {}
        
        # Keywords to identify key sections
        section_keywords = {
            'income_statement': ['income statement', 'statement of profit or loss', 'statement of comprehensive income'],
            'balance_sheet': ['statement of financial position', 'balance sheet'],
            'equity_statement': ['statement of changes in equity'],
            'highlights': ['performance highlights', 'financial highlights', 'key performance indicators'],
            'shareholder_info': ['shareholder information', 'shareholder analysis', 'top 20 shareholders', 'largest shareholders']
        }
        
        # Check a sample of pages throughout the document
        step = max(1, num_pages // 20)
        pages_to_check = list(range(0, min(num_pages, 300), step))
        
        # Add early pages as they often contain highlights
        pages_to_check.extend(range(1, 30))
        
        # Add pages where financial statements typically appear
        pages_to_check.extend(range(170, 210))
        
        # Remove duplicates and sort
        pages_to_check = sorted(list(set([p for p in pages_to_check if p < num_pages])))
        
        for page_num in pages_to_check:
            try:
                # Extract text from the page with a timeout
                try:
                    import signal
                    from contextlib import contextmanager

                    @contextmanager
                    def timeout(seconds):
                        def handler(signum, frame):
                            raise TimeoutError(f"Extraction timed out after {seconds} seconds")
                        
                        # Only use signal on systems that support it (not Windows)
                        if hasattr(signal, 'SIGALRM'):
                            original_handler = signal.signal(signal.SIGALRM, handler)
                            signal.alarm(seconds)
                        try:
                            yield
                        finally:
                            if hasattr(signal, 'SIGALRM'):
                                signal.alarm(0)
                                signal.signal(signal.SIGALRM, original_handler)
                    
                    # Use timeout only on platforms that support it
                    if hasattr(signal, 'SIGALRM'):
                        with timeout(5):  # 5 second timeout
                            text = extract_text(pdf_path, page_numbers=[page_num]).lower()
                    else:
                        # On Windows, just try to extract with normal exception handling
                        text = extract_text(pdf_path, page_numbers=[page_num], maxpages=1).lower()
                except (TimeoutError, KeyboardInterrupt):
                    logger.warning(f"Text extraction timed out on page {page_num}")
                    continue
                
                # Check for section keywords
                for section, keywords in section_keywords.items():
                    if any(keyword in text for keyword in keywords):
                        key_pages[section] = page_num
                        break
                
            except Exception as e:
                logger.debug(f"Error identifying sections on page {page_num}: {e}")
        
        return key_pages
    
    def _extract_from_tables(self, pdf_path, pages, metric_name):
        """Extract a metric from tables on the specified pages."""
        keyword_scores = {}  # Store page scores to find most relevant page
        values = []
        
        # Get keywords for this metric
        keywords = self.metric_keywords.get(metric_name, [])
        if not keywords:
            return None
        
        for page_num in pages:
            try:
                tables = camelot.read_pdf(pdf_path, pages=str(page_num+1), flavor='stream')
                
                for i, table in enumerate(tables):
                    df = table.df
                    
                    # Convert to string for easier searching
                    table_str = df.to_string().lower()
                    
                    # Calculate relevance score for this table
                    score = 0
                    for keyword in keywords:
                        if keyword in table_str:
                            score += 1
                    
                    if score > 0:
                        # This table contains relevant keywords
                        # Try to find the specific row with the metric
                        for i, row in df.iterrows():
                            row_str = ' '.join(str(cell).lower() for cell in row).strip()
                            if any(keyword in row_str for keyword in keywords):
                                # Try to extract the value
                                value = self._extract_numeric_value(row)
                                if value is not None:
                                    # Check if value is in millions
                                    if "million" in row_str or "mn" in row_str:
                                        values.append(value)  # Already in millions
                                    elif "billion" in row_str or "bn" in row_str:
                                        values.append(value * 1000)  # Convert billions to millions
                                    elif value > 100000:  
                                        # Value might be in absolute terms, convert to millions
                                        values.append(value / 1000)  # Convert thousands to millions
                                    else:
                                        values.append(value)
                        
                        # Store the score for this page
                        keyword_scores[page_num] = score
                
            except Exception as e:
                logger.debug(f"Error extracting tables from page {page_num}: {e}")
        
        if not values:
            return None
        
        # For revenue, cost of sales, find value in appropriate range
        if metric_name in ['revenue', 'cost_of_sales']:
            # Values should be in millions, and in the range of 10,000-500,000
            valid_values = [v for v in values if 50 <= v <= 500000]
            if valid_values:
                # First check the most relevant page
                if keyword_scores:
                    most_relevant_page = max(keyword_scores.items(), key=lambda x: x[1])[0]
                    # Look for values from the most relevant page
                    page_values = []
                    for page_num in pages:
                        try:
                            tables = camelot.read_pdf(pdf_path, pages=str(most_relevant_page+1), flavor='stream')
                            for table in tables:
                                for i, row in table.df.iterrows():
                                    row_str = ' '.join(str(cell).lower() for cell in row).strip()
                                    if any(keyword in row_str for keyword in keywords):
                                        value = self._extract_numeric_value(row)
                                        if value is not None:
                                            if "million" in row_str or "mn" in row_str:
                                                page_values.append(value)
                                            elif "billion" in row_str or "bn" in row_str:
                                                page_values.append(value * 1000)
                                            elif value > 100000:
                                                page_values.append(value / 1000)
                                            else:
                                                page_values.append(value)
                        except Exception:
                            pass
                    
                    if page_values:
                        valid_page_values = [v for v in page_values if 50 <= v <= 500000]
                        if valid_page_values:
                            return max(valid_page_values)
                
                # If we couldn't find a valid value from the most relevant page, use the largest valid value
                return max(valid_values)
            else:
                # If no values in typical range, take the largest value
                return max(values)
        
        # For EPS, prioritize typical values
        if metric_name == 'eps':
            # Typical EPS values are between 0.5 and 50
            typical_eps = [v for v in values if 0.5 <= v <= 50]
            if typical_eps:
                return max(typical_eps)
            return values[0] if values else None
        
        # For net asset per share, look for typical values
        if metric_name == 'net_asset_per_share':
            # Typical NAV values are between 50 and 300
            typical_nav = [v for v in values if 50 <= v <= 300]
            if typical_nav:
                return max(typical_nav)
            return values[0] if values else None
        
        # For other metrics, take the most common value or the largest
        if len(values) > 1:
            value_counts = {}
            for value in values:
                value_counts[value] = value_counts.get(value, 0) + 1
            most_common = max(value_counts.items(), key=lambda x: x[1])
            return most_common[0]
        
        return values[0] if values else None
    
    def _extract_metric_from_page(self, pdf_path, page_num, metric_name):
        """Extract a specific metric from a page using improved regex patterns."""
        values = []
        
        # Get pattern for this metric
        pattern = self.metric_patterns.get(metric_name)
        if not pattern:
            # Fall back to general extraction if no specific pattern is defined
            return self._general_metric_extraction(pdf_path, page_num, metric_name)
        
        # Try to extract from text using regex pattern
        try:
            text = extract_text(pdf_path, page_numbers=[page_num])
            text = text.lower()
            
            # Use the improved regex pattern
            matches = re.findall(pattern, text)
            
            # Log the matches for debugging
            if matches:
                logger.info(f"Found {len(matches)} matches for {metric_name} on page {page_num}: {matches}")
            
            for match in matches:
                # Handle tuple matches (pattern with capture groups)
                if isinstance(match, tuple):
                    # For 'operating_expenses', we're interested in the second capture group
                    if metric_name == 'operating_expenses':
                        if len(match) > 1 and isinstance(match[1], str) and re.match(r'[\d,\.]+', match[1]):
                            try:
                                val = float(match[1].replace(',', ''))
                                context_start = max(0, text.find(match[1]) - 50)
                                context_end = min(len(text), text.find(match[1]) + len(match[1]) + 50)
                                context = text[context_start:context_end]
                                
                                processed_val = self._process_value_with_units(val, context, metric_name)
                                if processed_val is not None:
                                    values.append(processed_val)
                                    logger.info(f"Extracted {metric_name} value: {processed_val} from '{match[0]} expenses'")
                            except ValueError:
                                continue
                    else:
                        # For other metrics, check all elements in the tuple
                        for item in match:
                            if isinstance(item, str) and re.match(r'[\d,\.]+', item):
                                try:
                                    val = float(item.replace(',', ''))
                                    context_start = max(0, text.find(item) - 50)
                                    context_end = min(len(text), text.find(item) + len(item) + 50)
                                    context = text[context_start:context_end]
                                    
                                    processed_val = self._process_value_with_units(val, context, metric_name)
                                    if processed_val is not None:
                                        values.append(processed_val)
                                        logger.info(f"Extracted {metric_name} value: {processed_val}")
                                except ValueError:
                                    continue
                else:
                    # Single match
                    try:
                        val = float(match.replace(',', ''))
                        context_start = max(0, text.find(match) - 50)
                        context_end = min(len(text), text.find(match) + len(match) + 50)
                        context = text[context_start:context_end]
                        
                        processed_val = self._process_value_with_units(val, context, metric_name)
                        if processed_val is not None:
                            values.append(processed_val)
                            logger.info(f"Extracted {metric_name} single value: {processed_val}")
                    except ValueError:
                        continue
        except Exception as e:
            logger.debug(f"Error extracting {metric_name} from text on page {page_num}: {e}")
        
        # Also try to extract from tables
        table_values = self._extract_from_tables_on_page(pdf_path, page_num, metric_name)
        if table_values:
            values.extend(table_values)
            logger.info(f"Added {len(table_values)} values from tables for {metric_name}")
        
        # No value found
        if not values:
            return None
        
        # Process values based on the metric type
        return self._select_best_value(values, metric_name)
    
    def _process_value_with_units(self, value, context, metric_name):
        """Process a value considering its context for units (millions, billions, etc.)"""
        if "million" in context or "mn" in context or "m" in context:
            # Value is already in millions
            return value
        elif "billion" in context or "bn" in context or "b" in context:
            # Convert billions to millions
            return value * 1000
        
        # For specific metrics, handle unit conversions
        if metric_name in ['revenue', 'cost_of_sales', 'operating_expenses']:
            if value > 100000:  
                # Value is likely in thousands, convert to millions
                return value / 1000
            elif value > 1000000:
                # Value is in absolute numbers, convert to millions
                return value / 1000000
        
        # For EPS and similar metrics, values are typically small
        if metric_name in ['eps', 'net_asset_per_share']:
            if value > 1000:
                # EPS values over 1000 are likely in cents or smaller units
                return value / 100
        
        return value
    
    def _extract_from_tables_on_page(self, pdf_path, page_num, metric_name):
        """Extract a metric from tables on a specific page."""
        values = []
        
        # Get keywords for this metric
        keywords = self.metric_keywords.get(metric_name, [])
        if not keywords:
            return None
        
        try:
            tables = camelot.read_pdf(pdf_path, pages=str(page_num+1), flavor='stream')
            
            for table in tables:
                # Convert to string for easier searching
                table_str = table.df.to_string().lower()
                
                # Check for keywords
                for keyword in keywords:
                    if keyword in table_str:
                        # Find rows with the keyword
                        for i, row in table.df.iterrows():
                            row_str = ' '.join(str(cell).lower() for cell in row).strip()
                            if keyword in row_str:
                                # Try to extract the value
                                value = self._extract_numeric_value(row)
                                if value is not None:
                                    # Check context for units
                                    context = row_str
                                    processed_val = self._process_value_with_units(value, context, metric_name)
                                    if processed_val is not None:
                                        values.append(processed_val)
        except Exception as e:
            logger.debug(f"Error extracting {metric_name} from table on page {page_num}: {e}")
        
        return values
    
    def _general_metric_extraction(self, pdf_path, page_num, metric_name):
        """Fall back to general extraction for metrics without specific patterns."""
        values = []
        
        # Get keywords for this metric
        keywords = self.metric_keywords.get(metric_name, [])
        if not keywords:
            return None
        
        try:
            text = extract_text(pdf_path, page_numbers=[page_num])
            text = text.lower()
            
            # Look for patterns with keywords
            for keyword in keywords:
                # Pattern for values with currency indicators and possibly "million" or "bn" indicators
                patterns = [
                    rf'{keyword}\s*(?:of|:)?\s*(?:Rs\.?|LKR)?\s*([\d,]+(?:\.\d+)?)\s*(?:million|mn)?',
                    rf'{keyword}.*?(?:Rs\.?|LKR)?\s*([\d,]+(?:\.\d+)?)\s*(?:million|mn)?',
                    rf'{keyword}.*?(?:Rs\.?|LKR|rupees).*?([\d,]+(?:\.\d+)?)\s*(?:million|mn)?',
                    # For values potentially shown as "140,043" without explicitly saying "million"
                    rf'{keyword}.*?([\d,]+(?:\.\d+)?)'
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, text)
                    for match in matches:
                        try:
                            val = float(match.replace(',', ''))
                            context_start = max(0, text.find(match) - 50)
                            context_end = min(len(text), text.find(match) + len(match) + 50)
                            context = text[context_start:context_end]
                            
                            processed_val = self._process_value_with_units(val, context, metric_name)
                            if processed_val is not None:
                                values.append(processed_val)
                        except ValueError:
                            continue
        except Exception as e:
            logger.debug(f"Error in general extraction for {metric_name} on page {page_num}: {e}")
        
        # No value found
        if not values:
            return None
        
        # Process values based on the metric type
        return self._select_best_value(values, metric_name)
    
    def _select_best_value(self, values, metric_name):
        """Select the best value from a list of candidates based on the metric type."""
        if not values:
            return None
            
        # For revenue, cost of sales, operating expenses - find value in appropriate range
        if metric_name in ['revenue', 'cost_of_sales', 'operating_expenses']:
            # Values should be in millions, and in a reasonable range
            valid_values = [v for v in values if 50 <= v <= 500000]
            if valid_values:
                # Use the most common value if there are duplicates, otherwise use max
                value_counts = {}
                for value in valid_values:
                    value_counts[value] = value_counts.get(value, 0) + 1
                
                if max(value_counts.values()) > 1:
                    # There are duplicates, use the most common
                    return max(value_counts.items(), key=lambda x: x[1])[0]
                else:
                    # No duplicates, use the highest value
                    return max(valid_values)
            else:
                # If no values in typical range, take the largest value
                return max(values)
        
        # For EPS and NAV, look for typical values
        if metric_name == 'eps':
            # Typical EPS values are between 0.5 and 50
            typical_eps = [v for v in values if 0.5 <= v <= 50]
            if typical_eps:
                # Find the most commonly occurring value if there are duplicates
                if len(typical_eps) > 1:
                    value_counts = {}
                    for value in typical_eps:
                        value_counts[value] = value_counts.get(value, 0) + 1
                    
                    if max(value_counts.values()) > 1:
                        return max(value_counts.items(), key=lambda x: x[1])[0]
                
                return max(typical_eps)
            return values[0]
        
        if metric_name == 'net_asset_per_share':
            # Typical NAV values are between 50 and 300
            typical_nav = [v for v in values if 50 <= v <= 300]
            if typical_nav:
                if len(typical_nav) > 1:
                    value_counts = {}
                    for value in typical_nav:
                        value_counts[value] = value_counts.get(value, 0) + 1
                    
                    if max(value_counts.values()) > 1:
                        return max(value_counts.items(), key=lambda x: x[1])[0]
                
                return max(typical_nav)
            return values[0]
        
        # For gross profit margin, values should be between 0 and 100
        if metric_name == 'gross_profit_margin':
            typical_margins = [v for v in values if 0 <= v <= 100]
            if typical_margins:
                return sum(typical_margins) / len(typical_margins)  # Average of valid margins
            return values[0]
        
        # For other metrics, take the most common value
        if len(values) > 1:
            value_counts = {}
            for value in values:
                value_counts[value] = value_counts.get(value, 0) + 1
            
            # Return the most frequent value
            return max(value_counts.items(), key=lambda x: x[1])[0]
        
        return values[0]
    
    def _extract_operating_expenses(self, pdf_path, pages_to_check):
        """Extract operating expenses from components: admin, selling & other."""
        components_needed = [
            "administrative expenses",
            "selling and distribution expenses",
            "other operating expenses"
        ]

        values = {}

        for page in pages_to_check:
            try:
                # TEXT SEARCH FIRST
                text = extract_text(pdf_path, page_numbers=[page]).lower()
                for label in components_needed:
                    if label in values:
                        continue
                    pattern = rf"{label}[^a-zA-Z0-9]*([\d,]+(?:\.\d+)?)"
                    matches = re.findall(pattern, text)
                    if matches:
                        for match in matches:
                            try:
                                num = float(match.replace(',', ''))
                                context = text[max(0, text.find(match) - 50):min(len(text), text.find(match) + 50)]
                                # Convert to millions if needed
                                if "billion" in context or "bn" in context:
                                    num *= 1000  # Convert billions to millions
                                elif num > 100000:  # Large number likely in thousands
                                    num /= 1000  # Convert to millions
                                
                                values[label] = num
                                logger.info(f"[TEXT] Found {label}: {num} on page {page}")
                                break
                            except ValueError:
                                continue

                # TABLE SEARCH AS BACKUP
                tables = camelot.read_pdf(pdf_path, pages=str(page+1), flavor='stream')
                for table in tables:
                    for i, row in table.df.iterrows():
                        row_text = ' '.join(str(cell).lower() for cell in row)
                        for label in components_needed:
                            if label in values:
                                continue
                            if label in row_text:
                                # Find numeric values in the row
                                nums = re.findall(r'([\d,]+(?:\.\d+)?)', row_text)
                                for num_str in nums:
                                    try:
                                        num = float(num_str.replace(',', ''))
                                        # Apply unit conversion based on context
                                        if "million" in row_text or "mn" in row_text:
                                            num = num  # Already in millions
                                        elif "billion" in row_text or "bn" in row_text:
                                            num *= 1000  # Convert billions to millions
                                        elif num > 100000:  # Likely in thousands
                                            num /= 1000  # Convert to millions
                                        
                                        values[label] = num
                                        logger.info(f"[TABLE] Found {label}: {num} on page {page}")
                                        break
                                    except ValueError:
                                        continue
            except Exception as e:
                logger.debug(f"Error extracting from page {page}: {e}")

        # Final sum if we found multiple components
        if len(values) >= 1:  # Even if we only find one component, return it
            total = sum(values.values())
            logger.info(f"Operating Expense Components: {values}")
            logger.info(f"Total Operating Expenses: {total}")
            return total

        # Look for direct "operating expenses" value
        for page in pages_to_check:
            try:
                text = extract_text(pdf_path, page_numbers=[page]).lower()
                pattern = r"(?:total\s+)?operating\s+expenses?[^a-zA-Z0-9]*([\d,]+(?:\.\d+)?)"
                matches = re.findall(pattern, text)
                if matches:
                    for match in matches:
                        try:
                            val = float(match.replace(',', ''))
                            context = text[max(0, text.find(match) - 50):min(len(text), text.find(match) + 50)]
                            # Convert to millions if needed
                            if "billion" in context or "bn" in context:
                                val *= 1000  # Convert billions to millions
                            elif val > 100000:  # Large number likely in thousands
                                val /= 1000  # Convert to millions
                            
                            logger.info(f"Found direct operating expenses: {val} on page {page}")
                            return val
                        except ValueError:
                            continue
            except Exception as e:
                logger.debug(f"Error extracting direct operating expenses from page {page}: {e}")

        logger.warning("Could not extract operating expenses.")
        return None

    def _extract_and_save_shareholders_info(self, session, report_id, pdf_path, pages_to_check):
        """
        Extracts Top 20 Shareholder data from tables using flexible parsing and saves it.
        Returns the number of shareholders successfully saved.
        """
        shareholders_saved_count = 0
        keywords = self.metric_keywords['top_20_shareholders']

        for page in pages_to_check:
            try:
                tables = camelot.read_pdf(pdf_path, pages=str(page + 1), flavor='stream', edge_tol=500)

                for table_idx, table in enumerate(tables):
                    df = table.df
                    table_str = df.to_string().lower()

                    # Check if table seems relevant based on keywords
                    if not any(keyword in table_str for keyword in keywords):
                        continue # Skip table if keywords not found

                    logger.info(f"Found potential shareholder table on page {page}, table index {table_idx}")

                    # --- Flexible Column Identification ---
                    rank_col, name_col, shares_col, percent_col = -1, -1, -1, -1
                    header_row_idx = -1

                    # 1. Try finding common headers in the first few rows
                    for r_idx in range(min(3, len(df))): # Check first 3 rows for headers
                        row_vals = [str(cell).lower().strip() for cell in df.iloc[r_idx]]
                        possible_rank = [i for i, h in enumerate(row_vals) if h in ['#', 'rank', 'no.', 's/n']]
                        possible_name = [i for i, h in enumerate(row_vals) if h in ['name', 'shareholder', 'investor']]
                        possible_shares = [i for i, h in enumerate(row_vals) if 'shares' in h or 'shareholding' in h and '%' not in h]
                        possible_percent = [i for i, h in enumerate(row_vals) if '%' in h or 'percentage' in h]

                        # If we found plausible candidates for most columns, assume this is the header
                        if len(possible_name) > 0 and len(possible_shares) > 0 and len(possible_percent) > 0:
                            rank_col = possible_rank[0] if possible_rank else -1 # Rank is optional
                            name_col = possible_name[0]
                            shares_col = possible_shares[0]
                            percent_col = possible_percent[0]
                            header_row_idx = r_idx
                            logger.info(f"Identified headers via text: Rank={rank_col}, Name={name_col}, Shares={shares_col}, Percent={percent_col} in row {header_row_idx}")
                            break

                    # 2. If headers not found, try guessing based on data types/patterns
                    if header_row_idx == -1:
                        logger.warning(f"Could not identify headers textually. Attempting heuristic identification.")
                        potential_cols = {'rank': [], 'name': [], 'shares': [], 'percent': []}
                        # Scan a few data rows to guess column types
                        for r_idx in range(len(df)):
                             # Skip potential header rows if they look non-numeric
                            if r_idx < 3 and any(str(df.iloc[r_idx, c]).isalpha() for c in range(df.shape[1])):
                                continue
                            for c_idx in range(df.shape[1]):
                                cell_val = str(df.iloc[r_idx, c_idx]).strip()
                                # Rank: Small integer, often first column
                                if c_idx <= 1 and cell_val.isdigit() and 1 <= int(cell_val) <= 50:
                                    potential_cols['rank'].append(c_idx)
                                # Name: Primarily text, not purely numeric
                                elif not cell_val.replace(',', '').replace('.', '').isdigit() and len(cell_val) > 3:
                                     potential_cols['name'].append(c_idx)
                                # Shares: Large number, contains commas
                                elif ',' in cell_val and cell_val.replace(',', '').isdigit():
                                    potential_cols['shares'].append(c_idx)
                                # Percent: Number between 0-100, might have '%' or '.'
                                elif '%' in cell_val or (cell_val.replace('.', '', 1).isdigit() and 0 <= float(cell_val.replace('%','')) <= 100):
                                     potential_cols['percent'].append(c_idx)

                        # Find the most likely column index for each type
                        from collections import Counter
                        if potential_cols['rank']: rank_col = Counter(potential_cols['rank']).most_common(1)[0][0]
                        if potential_cols['name']: name_col = Counter(potential_cols['name']).most_common(1)[0][0]
                        if potential_cols['shares']: shares_col = Counter(potential_cols['shares']).most_common(1)[0][0]
                        if potential_cols['percent']: percent_col = Counter(potential_cols['percent']).most_common(1)[0][0]
                        header_row_idx = 0 # Assume data starts from the top if guessing
                        logger.info(f"Identified headers heuristically: Rank={rank_col}, Name={name_col}, Shares={shares_col}, Percent={percent_col}")

                    # Check if we have the essential columns
                    if name_col == -1 or shares_col == -1 or percent_col == -1:
                        logger.error(f"Failed to identify essential columns (Name, Shares, Percent) for table on page {page}. Skipping.")
                        continue

                    # --- Process Rows ---
                    start_row = header_row_idx + 1 if header_row_idx != -1 else 0
                    for i in range(start_row, len(df)):
                        row_data = df.iloc[i]
                        try:
                            # Extract data using identified column indices
                            rank_val = int(row_data.iloc[rank_col]) if rank_col != -1 else None
                            name_val = str(row_data.iloc[name_col]).strip()
                            shares_str = str(row_data.iloc[shares_col]).replace(',', '').strip()
                            percent_str = str(row_data.iloc[percent_col]).replace('%', '').strip()

                            # Basic validation and type conversion
                            if not name_val or not shares_str or not percent_str:
                                logger.debug(f"Skipping row {i} due to missing data: Rank={rank_val}, Name={name_val}, Shares={shares_str}, Percent={percent_str}")
                                continue

                            shares_val = int(shares_str) if shares_str else None
                            percent_val = float(percent_str) if percent_str else None

                            # Further validation (e.g., name shouldn't be purely numeric)
                            if name_val.isdigit():
                                logger.debug(f"Skipping row {i} as name '{name_val}' appears numeric.")
                                continue

                            # Save valid data
                            if name_val and shares_val is not None and percent_val is not None:
                                shareholder = ShareholderData(
                                    report_id=report_id,
                                    rank=rank_val,
                                    shareholder_name=name_val,
                                    number_of_shares=shares_val,
                                    percentage_holding=percent_val
                                )
                                session.add(shareholder)
                                shareholders_saved_count += 1
                                # Commit periodically
                                if shareholders_saved_count % 20 == 0:
                                    session.commit()
                                    logger.info(f"Committed batch of 20 shareholders. Total saved: {shareholders_saved_count}")


                        except (IndexError, ValueError, TypeError) as row_err:
                            logger.warning(f"Error processing row {i} in shareholder table on page {page}: {row_err}. Row data: {row_data.tolist()}")
                            continue # Skip to next row

                    # Break after processing the first relevant table found on the page (can be adjusted)
                    if shareholders_saved_count > 0:
                        logger.info(f"Finished processing shareholder table on page {page}. Found {shareholders_saved_count} entries.")
                        break # Assume only one main shareholder table per page for now

            except Exception as e:
                logger.error(f"Error processing shareholder tables on page {page}: {e}")

        # Final commit
        if session.new:
            session.commit()

        if shareholders_saved_count == 0:
             logger.warning(f"Could not extract any structured shareholder data for report {report_id} using flexible parsing.")

        logger.info(f"Total shareholders saved for report {report_id}: {shareholders_saved_count}")
        return shareholders_saved_count

    def _extract_and_save_right_issues_info(self, session, report_id, metric_id, pdf_path, pages_to_check):
        """
        Extracts Right Issues details (ratio, price) using regex and saves to notes.
        Returns the extracted notes string if successful, otherwise None.
        """
        keywords = self.metric_keywords['right_issues']
        extracted_details = []

        # Regex patterns to find ratio and price near keywords
        # Ratio: Look for patterns like "X for Y", "X : Y", "one for every Y"
        ratio_pattern = r'(?:ratio\s+of|basis\s+of)\s+(\d+)\s*(?:for|:)\s*every\s*(\d+)'
        # Price: Look for patterns like "at LKR X", "price of Rs. Y", "subscription price Z"
        price_pattern = r'(?:at|price\s+of|subscription\s+price)\s*(?:lkr|rs\.?)\s*([\d,]+\.?\d*)'

        found_info = False
        for page in pages_to_check:
            try:
                text = extract_text(pdf_path, page_numbers=[page])
                text_lower = text.lower()

                # Check if page contains keywords
                if any(keyword in text_lower for keyword in keywords):
                    logger.info(f"Found potential 'Right Issues' keywords on page {page}")

                    # Search for ratio and price within a context window around the keyword
                    for keyword in keywords:
                         for match in re.finditer(keyword, text_lower):
                            start, end = match.span()
                            context_window = text[max(0, start - 200):min(len(text), end + 200)] # Search 200 chars around keyword

                            ratio_match = re.search(ratio_pattern, context_window, re.IGNORECASE)
                            price_match = re.search(price_pattern, context_window, re.IGNORECASE)

                            details = []
                            if ratio_match:
                                ratio_str = f"Ratio: {ratio_match.group(1)} for {ratio_match.group(2)}"
                                details.append(ratio_str)
                                logger.info(f"Extracted Right Issue Ratio: '{ratio_str}' on page {page}")
                                found_info = True
                            if price_match:
                                price_str = f"Price: LKR {price_match.group(1)}"
                                details.append(price_str)
                                logger.info(f"Extracted Right Issue Price: '{price_str}' on page {page}")
                                found_info = True

                            if details:
                                extracted_details.extend(details)

                    # If we found info on this page, we might not need to check others
                    # (Depends on how info is presented - could be multiple issues)
                    # For now, let's continue searching all relevant pages
            except Exception as e:
                logger.error(f"Error processing page {page} for right issues: {e}")

        # Combine unique findings and save
        final_notes = None
        if extracted_details:
            # Remove duplicates while preserving order (if possible)
            unique_details = []
            seen = set()
            for item in extracted_details:
                if item not in seen:
                    unique_details.append(item)
                    seen.add(item)
            final_notes = "; ".join(unique_details)
            logger.info(f"Final extracted Right Issues notes for report {report_id}: {final_notes}")
        else:
            logger.warning(f"Could not extract specific Right Issues details for report {report_id}")
            final_notes = "No specific details found." # Default note if nothing extracted

        # Save to YearlyData (Value remains 0.0 or null, notes contain details)
        try:
            # Check if entry exists, update notes; otherwise create new
            existing_entry = session.query(YearlyData).filter(
                YearlyData.report_id == report_id,
                YearlyData.metric_id == metric_id
            ).first()

            if existing_entry:
                existing_entry.notes = final_notes
                logger.info(f"Updating notes for existing Right Issues entry (Report ID: {report_id})")
            else:
                yearly_data = YearlyData(
                    report_id=report_id,
                    metric_id=metric_id,
                    value=0.0, # Keep value as 0.0 as per original schema intent
                    notes=final_notes
                )
                session.add(yearly_data)
                logger.info(f"Creating new Right Issues entry with notes (Report ID: {report_id})")

            session.commit()
            return final_notes # Return the notes string if successful

        except Exception as e:
            session.rollback()
            logger.error(f"Error saving Right Issues notes for report {report_id}: {e}")
            return None


    def _calculate_gross_profit_margin(self, session, report_id, metrics_db):
        """Calculate gross profit margin from revenue and cost of sales."""
        try:
            # Get revenue
            revenue_data = session.query(YearlyData).filter(
                YearlyData.report_id == report_id,
                YearlyData.metric_id == metrics_db['revenue'].id
            ).first()
            
            # Get cost of sales
            cost_data = session.query(YearlyData).filter(
                YearlyData.report_id == report_id,
                YearlyData.metric_id == metrics_db['cost_of_sales'].id
            ).first()
            
            # Calculate gross profit margin
            if revenue_data and cost_data and revenue_data.value > 0:
                revenue = revenue_data.value
                cost = cost_data.value
                gross_profit = revenue - cost
                margin = (gross_profit / revenue) * 100
                
                # Validate the margin - realistic values should be between 0 and 100%
                if margin < -10 or margin > 100:
                    logger.warning(f"Calculated gross profit margin {margin:.2f}% seems incorrect. "
                                  f"Revenue: {revenue}, Cost: {cost}")
                    # Check if values might be in different units (e.g., one in thousands, one in millions)
                    if revenue < 100 and cost > 10000:
                        # Revenue might be in billions, cost in millions
                        adjusted_revenue = revenue * 1000
                        adjusted_margin = ((adjusted_revenue - cost) / adjusted_revenue) * 100
                        if 0 <= adjusted_margin <= 100:
                            logger.info(f"Adjusted gross profit margin: {adjusted_margin:.2f}%")
                            margin = adjusted_margin
                    elif revenue > 10000 and cost < 100:
                        # Cost might be in billions, revenue in millions
                        adjusted_cost = cost * 1000
                        adjusted_margin = ((revenue - adjusted_cost) / revenue) * 100
                        if 0 <= adjusted_margin <= 100:
                            logger.info(f"Adjusted gross profit margin: {adjusted_margin:.2f}%")
                            margin = adjusted_margin
                
                # Save to database
                yearly_data = YearlyData(
                    report_id=report_id,
                    metric_id=metrics_db['gross_profit_margin'].id,
                    value=margin,
                    notes=f"Calculated as ((revenue - cost_of_sales) / revenue) * 100"
                )
                
                db.add_and_commit(session, yearly_data)
                logger.info(f"Calculated gross profit margin: {margin:.2f}%")
                return True
            else:
                logger.warning("Could not calculate gross profit margin - missing revenue or cost of sales")
        
        except Exception as e:
            logger.error(f"Error calculating gross profit margin: {e}")
        
        return False
    
    def _save_metric(self, session, report_id, metric_id, value, pdf_path):
        """Save a metric value to the database."""
        try:
            yearly_data = YearlyData(
                report_id=report_id,
                metric_id=metric_id,
                value=value,
                notes=f"Extracted from {os.path.basename(pdf_path)}"
            )
            db.add_and_commit(session, yearly_data)
            logger.info(f"Saved metric {metric_id} with value {value}")
        except Exception as e:
            logger.error(f"Error saving metric {metric_id} for report {report_id}: {e}")
    
    def _check_if_metric_exists(self, session, report_id, metric_id):
        """Check if a metric already exists for this report."""
        existing = session.query(YearlyData).filter(
            YearlyData.report_id == report_id,
            YearlyData.metric_id == metric_id
        ).first()
        
        return existing is not None
    
    def _extract_numeric_value(self, row):
        """Extract a numeric value from a table row."""
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
    
    def _get_page_count(self, pdf_path):
        """Get the number of pages in a PDF file using existing dependencies."""
        try:
            # Try using PDFMiner
            from pdfminer.pdfpage import PDFPage
            
            with open(pdf_path, 'rb') as file:
                count = sum(1 for _ in PDFPage.get_pages(file))
                return count
        except Exception as e:
            logger.error(f"Error getting page count with pdfminer: {e}")
            
            # Fallback to camelot for an estimate
            try:
                # Try with page 1 first to check if the file is valid
                camelot.read_pdf(pdf_path, pages='1', flavor='stream')
                
                # Use binary search approach to find approximate page count
                low = 1
                high = 500  # Reasonable upper limit for annual reports
                last_successful = 1
                
                while low <= high:
                    mid = (low + high) // 2
                    try:
                        camelot.read_pdf(pdf_path, pages=str(mid), flavor='stream')
                        last_successful = mid
                        low = mid + 1
                    except Exception:
                        high = mid - 1
                
                # last_successful is the highest page that worked
                return last_successful + 5  # Add a small buffer
            except Exception as e2:
                logger.error(f"Error estimating page count with camelot: {e2}")
                return 150  # Conservative default estimate

    def _extract_eps(self, pdf_path, pages_to_check):
        """
        Optimized: Robustly extract Earnings Per Share (EPS) from tables and text.
        - No hardcoded years, columns, or strict label requirements.
        - Always run both table and regex/text extraction and merge results.
        - Scan all rows/cells for any EPS-like label and extract all numbers.
        - Log all candidates and select the largest value in the typical range (0.5-50), else the largest found.
        """
        import re
        values = set()
        # --- TABLE EXTRACTION (very flexible) ---
        for page in pages_to_check:
            try:
                tables = camelot.read_pdf(pdf_path, pages=str(page+1), flavor='stream')
                for table in tables:
                    df = table.df
                    for _, row in df.iterrows():
                        row_str = ' '.join(str(cell).lower() for cell in row)
                        if 'eps' in row_str or 'earnings per share' in row_str:
                            # Extract all numbers in the row
                            for cell in row:
                                found = re.findall(r"[-+]?[0-9]*\.?[0-9]+", str(cell).replace(',', ''))
                                for match in found:
                                    try:
                                        val = float(match)
                                        if 0.1 <= val <= 100:
                                            values.add(val)
                                            logger.info(f"[TABLE] Extracted EPS candidate: {val} from page {page}")
                                    except Exception:
                                        continue
            except Exception as e:
                logger.debug(f"Error extracting EPS from table on page {page}: {e}")

        # --- REGEX/TEXT EXTRACTION (very flexible) ---
        for page in pages_to_check:
            try:
                text = extract_text(pdf_path, page_numbers=[page])
                text = text.lower()
                # Look for lines containing eps or earnings per share
                for line in text.split('\n'):
                    if 'eps' in line or 'earnings per share' in line:
                        found = re.findall(r"[-+]?[0-9]*\.?[0-9]+", line.replace(',', ''))
                        for match in found:
                            try:
                                val = float(match)
                                if 0.1 <= val <= 100:
                                    values.add(val)
                                    logger.info(f"[TEXT] Extracted EPS candidate: {val} from page {page}")
                            except Exception:
                                continue
            except Exception as e:
                logger.debug(f"Error extracting EPS from text on page {page}: {e}")

        # --- LOGGING & SELECTION ---
        values = list(values)
        logger.info(f"All candidate EPS values extracted: {values}")
        if values:
            typical_eps = [v for v in values if 0.5 <= v <= 50]
            if typical_eps:
                selected = max(typical_eps)
                logger.info(f"Selected EPS value (typical range 0.5-50): {selected}")
            else:
                selected = max(values)
                logger.warning(f"No EPS values in typical range 0.5-50. Using largest extracted value: {selected}")
            return selected
        else:
            logger.warning("No EPS values found for this report after all extraction attempts.")
            return None
    
    def _extract_net_asset_per_share(self, pdf_path, pages_to_check):
        """
        Extract Net Asset Value Per Share for the current report year only.
        Uses robust regex/table extraction, NO hardcoded years/pages/values, logs all candidates, and selects the best group.
        """
        import itertools
        possible_values = []
        nav_patterns = [
            # Flexible patterns to match NAV with or without currency, ~, etc.
            r"(?i)net\s+asset(?:s)?\s+(?:value\s+)?per\s+share[^\d\n]{0,30}(~?\s*rs\.?\s*)?([\d,.]+)",
            r"(?i)nav\s+per\s+share[^\d\n]{0,30}(~?\s*rs\.?\s*)?([\d,.]+)",
            r"(?i)book\s+value\s+per\s+share[^\d\n]{0,30}(~?\s*rs\.?\s*)?([\d,.]+)",
            r"(?i)(?:net worth|equity)\s+per\s+share[^\d\n]{0,30}(~?\s*rs\.?\s*)?([\d,.]+)",
            r"(?i)(?:rs\.?|lkr)?\s*([\d,.]+)[^\d\n]{0,30}(?:per share|per ordinary share|net asset)"
        ]
        for page in pages_to_check:
            try:
                text = extract_text(pdf_path, page_numbers=[page]).lower()
                for pattern in nav_patterns:
                    for match in re.finditer(pattern, text):
                        # Accept match from any capturing group that looks like a number
                        for group in match.groups():
                            if group and re.match(r"[\d,.]+", group):
                                try:
                                    val = float(group.replace(',', ''))
                                    if 10 <= val <= 1000:  # Broader range, but filter out obvious noise
                                        possible_values.append(val)
                                        logger.info(f"Found NAV: {val} on page {page} (pattern: {pattern})")
                                except ValueError:
                                    continue
                # Also check for NAV in tables
                try:
                    tables = camelot.read_pdf(pdf_path, pages=str(page + 1), flavor='stream')
                    for table in tables:
                        df = table.df
                        table_str = df.to_string().lower()
                        if 'net asset' in table_str and 'per share' in table_str:
                            for i, row in df.iterrows():
                                for cell in row:
                                    cell_str = str(cell).replace(',', '').strip()
                                    try:
                                        val = float(cell_str)
                                        if 10 <= val <= 1000:
                                            possible_values.append(val)
                                            logger.info(f"Found NAV from table: {val} on page {page}")
                                    except ValueError:
                                        continue
                except Exception as e:
                    logger.debug(f"Error extracting NAV from tables on page {page}: {e}")
            except Exception as e:
                logger.debug(f"Error extracting NAV from text on page {page}: {e}")
        # Log all candidates
        logger.info(f"All candidate NAV values extracted: {possible_values}")
        if possible_values:
            # Group values that are within 1.0 unit of each other
            possible_values.sort()
            groups = []
            for k, g in itertools.groupby(possible_values, key=lambda x: round(x)):
                groups.append(list(g))
            # Select the group with the most members, then pick the largest value in that group
            best_group = max(groups, key=len)
            best_value = max(best_group)
            logger.info(f"Selected NAV: {best_value} (group size: {len(best_group)})")
            return best_value
        logger.warning("No valid NAV values found for this report after all extraction attempts.")
        return None

def main():
    """Main function to run the extraction process."""
    try:
        # Get configuration
        config = get_config()
        pdf_directory = config.PDF_DIRECTORY
        
        logger.info(f"PDF directory path: {pdf_directory}")
        if not os.path.exists(pdf_directory):
            logger.error(f"PDF directory {pdf_directory} does not exist")
            # Try the relative path
            alternative_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data-pdf')
            logger.info(f"Trying alternative path: {alternative_path}")
            if os.path.exists(alternative_path):
                logger.info(f"Using alternative PDF directory: {alternative_path}")
                pdf_directory = alternative_path
            else:
                logger.error(f"Alternative PDF directory {alternative_path} also does not exist")
                return 1
        
        # Initialize the database
        db.init_db()
        
        # Create and run the extractor
        extractor = FinancialDataExtractor(pdf_directory)
        
        # Process all reports
        logger.info("Starting financial data extraction...")
        results = extractor.process_all_reports()
        
        # Log results
        logger.info(f"Extraction completed. Results: {results}")
        
        return 0
    
    except Exception as e:
        logger.error(f"Error in financial data extraction: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
