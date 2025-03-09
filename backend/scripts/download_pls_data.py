#!/usr/bin/env python3
"""
Script to download Public Libraries Survey (PLS) data from IMLS.
"""
import os
import sys
import requests
import logging
import re
from pathlib import Path
from tqdm import tqdm
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# IMLS data URLs
IMLS_BASE_URL = "https://www.imls.gov"
PLS_DATA_PAGE = "https://www.imls.gov/research-evaluation/data-collection/public-libraries-survey"

def find_pls_data_urls(year):
    """
    Find PLS data URLs for a specific year by scraping the IMLS website.
    """
    try:
        logger.info(f"Searching for PLS data URLs for year {year}")
        
        # Get the PLS data page
        response = requests.get(PLS_DATA_PAGE)
        response.raise_for_status()
        
        # Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find links to data files
        urls = {}
        year_pattern = f"fy{year}"
        
        # Look for links containing the year pattern
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.text.lower()
            
            # Check if the link is to a CSV file and contains the year pattern
            if href.endswith('.csv') and year_pattern in href.lower():
                # Determine the file type
                if 'outlet' in href.lower():
                    urls['outlet'] = IMLS_BASE_URL + href if not href.startswith('http') else href
                elif 'library' in href.lower():
                    urls['library'] = IMLS_BASE_URL + href if not href.startswith('http') else href
                elif 'state' in href.lower():
                    urls['state'] = IMLS_BASE_URL + href if not href.startswith('http') else href
        
        if not urls:
            # If no direct links found, look for download pages
            for link in soup.find_all('a', href=True):
                href = link['href']
                text = link.text.lower()
                
                if f"fy {year}" in text.lower() or f"fiscal year {year}" in text.lower():
                    # Follow this link to find data files
                    logger.info(f"Found potential data page: {href}")
                    download_page_url = IMLS_BASE_URL + href if not href.startswith('http') else href
                    urls = find_data_on_download_page(download_page_url, year)
                    if urls:
                        break
        
        if not urls:
            logger.error(f"No PLS data URLs found for year {year}")
            return None
        
        logger.info(f"Found PLS data URLs for year {year}: {urls}")
        return urls
    
    except Exception as e:
        logger.error(f"Error finding PLS data URLs: {e}")
        return None

def find_data_on_download_page(url, year):
    """
    Find data files on a download page.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        urls = {}
        year_pattern = f"fy{year}"
        
        # Look for links to CSV files
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Check if the link is to a CSV file and contains the year pattern
            if href.endswith('.csv') and year_pattern in href.lower():
                # Determine the file type
                if 'outlet' in href.lower():
                    urls['outlet'] = IMLS_BASE_URL + href if not href.startswith('http') else href
                elif 'library' in href.lower():
                    urls['library'] = IMLS_BASE_URL + href if not href.startswith('http') else href
                elif 'state' in href.lower():
                    urls['state'] = IMLS_BASE_URL + href if not href.startswith('http') else href
        
        return urls
    
    except Exception as e:
        logger.error(f"Error finding data on download page: {e}")
        return None

def download_file(url, destination):
    """
    Download a file from a URL to a destination with progress bar.
    """
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 Kibibyte
        
        logger.info(f"Downloading {url} to {destination}")
        
        with open(destination, 'wb') as file, tqdm(
            desc=os.path.basename(destination),
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(block_size):
                size = file.write(data)
                bar.update(size)
                
        logger.info(f"Successfully downloaded {destination}")
        return True
    except Exception as e:
        logger.error(f"Error downloading {url}: {e}")
        return False

def main():
    """
    Main function to download PLS data.
    """
    # Create data directory if it doesn't exist
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    
    # Get year from command line or use default
    year = sys.argv[1] if len(sys.argv) > 1 else "2021"
    
    # Find PLS data URLs for the specified year
    urls = find_pls_data_urls(year)
    
    if not urls:
        logger.error(f"No PLS data URLs found for year {year}")
        return
    
    # Create year directory
    year_dir = data_dir / year
    year_dir.mkdir(exist_ok=True)
    
    # Download files for the specified year
    for file_type, url in urls.items():
        file_name = f"pls_{year}_{file_type}.csv"
        destination = year_dir / file_name
        
        if destination.exists():
            logger.info(f"File {destination} already exists. Skipping download.")
            continue
            
        success = download_file(url, destination)
        if not success:
            logger.error(f"Failed to download {file_name}")
    
    logger.info(f"Download process completed for year {year}")

if __name__ == "__main__":
    main() 