#!/usr/bin/env python
"""
Extract top 20 shareholders data from John Keells Holdings PLC annual reports.
This script processes PDF files, extracts shareholder tables, and stores the data in the database.
"""

import os
import re
import sys
import camelot
import pdfminer
from pdfminer.high_level import extract_text
import pandas as pd
from pathlib import Path

# Add the backend directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

from models.financial_data import FinancialReport, ShareholderData
from database import Database
from config import Config

def find_shareholder_pages(pdf_path):
    """Find pages that likely contain shareholder information by searching for relevant keywords."""
    text = extract_text(pdf_path)
    text_by_page = text.split('\f')  # Split by form feed character to get pages
    
    potential_pages = []
    keywords = ['top 20 shareholders', 'twenty largest shareholders', 'major shareholders']
    
    for i, page_text in enumerate(text_by_page):
        page_text_lower = page_text.lower()
        for keyword in keywords:
            if keyword in page_text_lower:
                # Add a buffer of pages around the matched page for tables that might span pages
                start_page = max(1, i)
                end_page = min(len(text_by_page), i + 3)  # Look at this page and potentially the next 2
                potential_pages.extend(range(start_page, end_page + 1))
                break
    
    return sorted(set(potential_pages))  # Remove duplicates and sort

def extract_shareholders_table(pdf_path, pages):
    """Extract shareholder tables from the PDF using Camelot."""
    all_tables = []
    
    for page in pages:
        try:
            tables = camelot.read_pdf(pdf_path, pages=str(page), flavor='lattice')
            if len(tables) == 0:
                # Try stream flavor if lattice doesn't work
                tables = camelot.read_pdf(pdf_path, pages=str(page), flavor='stream')
            
            for table in tables:
                df = table.df
                # Check if this looks like a shareholder table
                if df.shape[1] >= 3 and any('share' in str(cell).lower() for cell in df.values.flatten()):
                    all_tables.append(df)
        except Exception as e:
            print(f"Error extracting tables from page {page}: {e}")
    
    return all_tables

def process_shareholder_table(df):
    """Process and clean the extracted shareholder table."""
    # Common column names in shareholder tables
    name_columns = ['name', 'shareholder', 'shareholders', 'name of the shareholder']
    shares_columns = ['shares', 'no. of shares', 'number of shares', 'share count']
    percentage_columns = ['%', 'percentage', 'holding', '% holding', 'percentage holding']
    
    # Normalize the column headers (make lowercase)
    df.columns = [str(col).lower().strip() for col in df.columns]
    
    # Try to identify the relevant columns
    name_col = next((i for i, col in enumerate(df.columns) if any(keyword in col for keyword in name_columns)), None)
    shares_col = next((i for i, col in enumerate(df.columns) if any(keyword in col for keyword in shares_columns)), None)
    pct_col = next((i for i, col in enumerate(df.columns) if any(keyword in col for keyword in percentage_columns)), None)
    
    # If we can't identify columns by name, try to use position
    if name_col is None or shares_col is None or pct_col is None:
        # Assume standard order: rank, name, shares, percentage
        if df.shape[1] >= 4:
            name_col = 1
            shares_col = 2
            pct_col = 3
        elif df.shape[1] >= 3:
            name_col = 0
            shares_col = 1
            pct_col = 2
    
    if name_col is None or shares_col is None or pct_col is None:
        return None  # Can't process this table
    
    # Extract and clean the data
    shareholders = []
    for i, row in df.iterrows():
        # Skip header rows or rows with no data
        if i == 0 or pd.isna(row.iloc[name_col]) or 'name' in str(row.iloc[name_col]).lower():
            continue
        
        name = str(row.iloc[name_col]).strip()
        
        # Extract share count, removing commas and converting to integer
        shares_str = str(row.iloc[shares_col]).replace(',', '').strip()
        shares = None
        try:
            shares_match = re.search(r'\d+', shares_str)
            if shares_match:
                shares = int(shares_match.group())
        except (ValueError, TypeError):
            pass
        
        # Extract percentage, removing % symbol and converting to float
        pct_str = str(row.iloc[pct_col]).replace('%', '').strip()
        percentage = None
        try:
            pct_match = re.search(r'\d+\.\d+|\d+', pct_str)
            if pct_match:
                percentage = float(pct_match.group())
        except (ValueError, TypeError):
            pass
        
        # Only add if we have valid data
        if name and (shares is not None or percentage is not None):
            rank = i  # Use row index as rank (adjust if needed)
            shareholders.append({
                'rank': rank,
                'name': name,
                'shares': shares,
                'percentage': percentage
            })
    
    # Sort by shares in case the table wasn't in order
    if shareholders:
        shareholders.sort(key=lambda x: x['shares'] if x['shares'] is not None else 0, reverse=True)
        # Re-rank after sorting
        for i, shareholder in enumerate(shareholders, 1):
            shareholder['rank'] = i
    
    return shareholders[:20]  # Return top 20 shareholders

def extract_year_from_filename(filename):
    """Extract the year from the filename."""
    year_match = re.search(r'20\d{2}', filename)
    if year_match:
        return int(year_match.group())
    return None

def save_to_database(year, shareholders_data, pdf_path):
    """Save the extracted shareholder data to the database."""
    db = Database()
    session = db.get_session()
    
    try:
        # Find or create the FinancialReport for this year
        report = session.query(FinancialReport).filter_by(year=year).first()
        if not report:
            report = FinancialReport(
                year=year,
                title=f"John Keells Holdings Annual Report {year}",
                file_path=pdf_path
            )
            session.add(report)
            session.commit()
        
        # Delete existing shareholder data for this report to avoid duplicates
        session.query(ShareholderData).filter_by(report_id=report.id).delete()
        
        # Add the new shareholder data
        for shareholder in shareholders_data:
            data = ShareholderData(
                report_id=report.id,
                rank=shareholder['rank'],
                shareholder_name=shareholder['name'],
                number_of_shares=shareholder['shares'],
                percentage_holding=shareholder['percentage']
            )
            session.add(data)
        
        session.commit()
        print(f"Saved {len(shareholders_data)} shareholders for year {year}")
        return True
    except Exception as e:
        session.rollback()
        print(f"Error saving to database: {e}")
        return False
    finally:
        session.close()

def main():
    """Main function to process PDF files and extract shareholder data."""
    pdf_dir = Config.PDF_DIR
    if not os.path.exists(pdf_dir):
        print(f"PDF directory does not exist: {pdf_dir}")
        return
    
    # Process each PDF file in the directory
    for filename in os.listdir(pdf_dir):
        if filename.lower().endswith('.pdf'):
            pdf_path = os.path.join(pdf_dir, filename)
            year = extract_year_from_filename(filename)
            
            if not year:
                print(f"Could not determine year from filename: {filename}")
                continue
            
            print(f"Processing PDF for year {year}: {filename}")
            
            # Find pages likely to contain shareholder information
            potential_pages = find_shareholder_pages(pdf_path)
            if not potential_pages:
                print(f"No potential shareholder pages found in {filename}")
                continue
            
            print(f"Found potential shareholder pages: {potential_pages}")
            
            # Extract tables from the potential pages
            tables = extract_shareholders_table(pdf_path, potential_pages)
            if not tables:
                print(f"No tables found on the potential pages in {filename}")
                continue
            
            # Process each table to find shareholder data
            for i, table in enumerate(tables):
                shareholders = process_shareholder_table(table)
                if shareholders and len(shareholders) > 5:  # Require at least 5 shareholders to be valid
                    print(f"Found {len(shareholders)} shareholders in table {i+1}")
                    success = save_to_database(year, shareholders, pdf_path)
                    if success:
                        print(f"Successfully saved shareholder data for {year}")
                        break  # Use the first good table we find
            else:
                print(f"No valid shareholder tables found in {filename}")

if __name__ == "__main__":
    main()
