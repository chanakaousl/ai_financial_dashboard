import os
import camelot
import pdfminer
from pdfminer.high_level import extract_text
import pandas as pd
import logging

# Configure logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFParser:
    """Utility class for parsing financial data from PDF reports."""
    
    def __init__(self, pdf_directory, flavor='lattice'):
        """
        Initialize the PDF parser.
        
        Args:
            pdf_directory (str): Directory containing PDF files
            flavor (str, optional): The table extraction method to use ('lattice' or 'stream'). 
                                   Use 'stream' to avoid Ghostscript dependency. Defaults to 'lattice'.
        """
        self.pdf_directory = pdf_directory
        self.flavor = flavor
        
    def list_pdf_files(self):
        """
        Return a list of PDF files in the specified directory.
        
        Returns:
            list: List of PDF file paths
        """
        pdf_files = []
        try:
            for file in os.listdir(self.pdf_directory):
                if file.endswith('.pdf'):
                    pdf_files.append(os.path.join(self.pdf_directory, file))
            return pdf_files
        except Exception as e:
            logger.error(f"Error listing PDF files: {e}")
            return []
    
    def extract_tables(self, pdf_path, pages='all'):
        """
        Extract tables from a PDF file using Camelot.
        
        Args:
            pdf_path (str): Path to the PDF file
            pages (str): Pages to extract tables from
            
        Returns:
            list: List of pandas DataFrames containing table data
        """
        try:
            # Use the specified flavor for extraction
            tables = camelot.read_pdf(pdf_path, pages=pages, flavor=self.flavor)
            
            # If no tables found or tables are empty, try with different settings but same flavor
            if len(tables) == 0 or all(len(table.df) == 0 for table in tables):
                if self.flavor == 'lattice':
                    # For lattice, try adjusting line_scale
                    tables = camelot.read_pdf(pdf_path, pages=pages, flavor=self.flavor, line_scale=40)
                else:
                    # For stream, try adjusting edge_tol
                    tables = camelot.read_pdf(pdf_path, pages=pages, flavor=self.flavor, edge_tol=500)
            
            # Filter out empty tables
            return [table.df for table in tables if len(table.df) > 0]
        except Exception as e:
            logger.error(f"Error extracting tables from {pdf_path}: {e}")
            return []
    
    def extract_text(self, pdf_path, start_page=1, end_page=None):
        """
        Extract text from a PDF file using PDFMiner.
        
        Args:
            pdf_path (str): Path to the PDF file
            start_page (int): First page to extract (1-indexed)
            end_page (int): Last page to extract (inclusive)
            
        Returns:
            str: Extracted text
        """
        try:
            if end_page is None:
                # Extract all pages
                return extract_text(pdf_path, page_numbers=None)
            else:
                # Extract specified page range
                return extract_text(pdf_path, page_numbers=range(start_page-1, end_page))
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {e}")
            return ""
    
    def search_keyword(self, pdf_path, keywords, context_size=100):
        """
        Search for keywords in a PDF and return context around matches.
        
        Args:
            pdf_path (str): Path to the PDF file
            keywords (list): List of keywords to search for
            context_size (int): Number of characters to include before and after match
            
        Returns:
            dict: Dictionary with keywords as keys and list of context strings as values
        """
        try:
            full_text = self.extract_text(pdf_path)
            results = {}
            
            for keyword in keywords:
                results[keyword] = []
                last_end = 0
                keyword_lower = keyword.lower()
                text_lower = full_text.lower()
                
                while True:
                    start_idx = text_lower.find(keyword_lower, last_end)
                    if start_idx == -1:
                        break
                        
                    context_start = max(0, start_idx - context_size)
                    context_end = min(len(full_text), start_idx + len(keyword) + context_size)
                    context = full_text[context_start:context_end]
                    
                    results[keyword].append(context)
                    last_end = start_idx + len(keyword)
                    
            return results
        except Exception as e:
            logger.error(f"Error searching for keywords in {pdf_path}: {e}")
            return {k: [] for k in keywords} 