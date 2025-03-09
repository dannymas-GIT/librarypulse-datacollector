import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from loguru import logger

# Set up logger
logger.add("discovery_test.log", rotation="10 MB")

IMLS_DATA_BASE_URL = "https://www.imls.gov/research-evaluation/data-collection/public-libraries-survey"

def discover_available_years():
    """
    Scrape the IMLS website to discover available PLS data years.
    
    Returns:
        List[int]: List of years with available data
    """
    logger.info(f"Discovering available PLS data years from {IMLS_DATA_BASE_URL}")
    
    try:
        response = requests.get(IMLS_DATA_BASE_URL)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for year patterns in the page
        year_links = []
        for heading in soup.find_all(['h2', 'h3', 'h4']):
            # Match patterns like "FY 2022" or just "2022"
            year_match = re.search(r'(FY\s*)?(\d{4})', heading.text)
            if year_match:
                year = int(year_match.group(2))
                if 1992 <= year <= datetime.now().year:  # Valid year range
                    year_links.append(year)
                    
                    # Try to find download links in the section
                    section = heading.find_next(['ul', 'div'])
                    if section:
                        for link in section.find_all('a', href=True):
                            if 'csv' in link.text.lower():
                                logger.info(f"Found potential CSV link for year {year}: {link.get('href')}")
        
        years = sorted(list(set(year_links)))
        logger.info(f"Discovered years: {years}")
        return years
    
    except Exception as e:
        logger.error(f"Error discovering available years: {str(e)}")
        return []

if __name__ == "__main__":
    print("Testing data discovery from IMLS website...")
    years = discover_available_years()
    
    if years:
        print(f"✓ Successfully discovered {len(years)} available years: {years}")
    else:
        print("✗ Failed to discover any years")
    
    print("\nFinished testing.") 