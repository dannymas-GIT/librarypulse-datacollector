#!/usr/bin/env python3
"""
Script to download Public Libraries Survey (PLS) data from IMLS or alternative sources.
"""
import os
import sys
import requests
import logging
import re
import time
import json
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

# Alternative data sources
DATA_GOV_API_BASE = "https://api.data.gov/ed/libraries"
DATA_GOV_API_KEY = os.getenv("DATA_GOV_API_KEY", "")  # You'll need to register for an API key

# Alternative download URLs (direct links to most recent data files)
ALTERNATIVE_URLS = {
    "2019": {
        "library": "https://www.imls.gov/sites/default/files/2022-02/pls_fy2019_library_rv.csv",
        "outlet": "https://www.imls.gov/sites/default/files/2022-02/pls_fy2019_outlet_rv.csv",
        "state": "https://www.imls.gov/sites/default/files/2022-02/pls_fy2019_state_rv.csv"
    },
    "2020": {
        "library": "https://www.imls.gov/sites/default/files/2022-08/pls_fy2020_library_rv.csv",
        "outlet": "https://www.imls.gov/sites/default/files/2022-08/pls_fy2020_outlet_rv.csv",
        "state": "https://www.imls.gov/sites/default/files/2022-08/pls_fy2020_state_rv.csv"
    },
    "2021": {
        "library": "https://www.imls.gov/sites/default/files/2023-07/pls_fy2021_library_rv.csv",
        "outlet": "https://www.imls.gov/sites/default/files/2023-07/pls_fy2021_outlet_rv.csv",
        "state": "https://www.imls.gov/sites/default/files/2023-07/pls_fy2021_state_rv.csv"
    }
}

def find_pls_data_urls_from_imls(year):
    """
    Find PLS data URLs for a specific year by scraping the IMLS website.
    """
    try:
        logger.info(f"Searching for PLS data URLs for year {year} from IMLS website")
        
        # Get the PLS data page with retries
        for attempt in range(3):
            try:
                response = requests.get(PLS_DATA_PAGE, timeout=10)
                response.raise_for_status()
                break
            except (requests.RequestException, requests.Timeout) as e:
                logger.warning(f"Attempt {attempt+1} failed to access IMLS website: {e}")
                if attempt == 2:  # Last attempt
                    logger.error("All attempts to access IMLS website failed")
                    return None
                time.sleep(2)  # Wait before retrying
        
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
        
        if urls:
            logger.info(f"Found PLS data URLs for year {year} from IMLS website: {urls}")
        else:
            logger.warning(f"No PLS data URLs found for year {year} from IMLS website")
            
        return urls
    
    except Exception as e:
        logger.error(f"Error finding PLS data URLs from IMLS website: {e}")
        return None

def find_data_on_download_page(url, year):
    """
    Find data files on a download page.
    """
    try:
        response = requests.get(url, timeout=10)
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

def get_data_from_datagov_api(year):
    """
    Try to fetch data from data.gov API as an alternative source.
    """
    if not DATA_GOV_API_KEY:
        logger.warning("No Data.gov API key provided. Skipping Data.gov API attempt.")
        return None
    
    try:
        logger.info(f"Attempting to fetch PLS data for year {year} from Data.gov API")
        
        # Construct the API URL for libraries data
        api_url = f"{DATA_GOV_API_BASE}/pls/{year}?api_key={DATA_GOV_API_KEY}&format=csv"
        
        response = requests.get(api_url, timeout=15)
        if response.status_code != 200:
            logger.warning(f"Data.gov API returned status code {response.status_code}")
            return None
            
        # Check if the response is actually CSV data
        if 'text/csv' not in response.headers.get('content-type', ''):
            logger.warning("Response from Data.gov API is not in CSV format")
            return None
            
        # Create a temporary directory to store the downloaded file
        temp_dir = Path(__file__).parent.parent / "data" / "temp"
        temp_dir.mkdir(exist_ok=True, parents=True)
        
        # Write the data to a temporary file
        temp_file = temp_dir / f"pls_{year}_library.csv"
        with open(temp_file, 'wb') as f:
            f.write(response.content)
            
        logger.info(f"Successfully downloaded library data from Data.gov API to {temp_file}")
        
        # Return URLs pointing to the local file
        return {
            "library": str(temp_file)
        }
    
    except Exception as e:
        logger.error(f"Error fetching data from Data.gov API: {e}")
        return None

def try_alternative_download_urls(year):
    """
    Try to download from known alternative URLs.
    """
    if str(year) not in ALTERNATIVE_URLS:
        logger.warning(f"No alternative URLs available for year {year}")
        return None
        
    logger.info(f"Trying alternative download URLs for year {year}")
    
    # Get the URLs for the specified year
    urls = ALTERNATIVE_URLS[str(year)]
    
    # Test each URL to make sure it's accessible
    valid_urls = {}
    for file_type, url in urls.items():
        try:
            # Just check the headers to see if the URL is valid
            response = requests.head(url, timeout=10)
            if response.status_code == 200:
                valid_urls[file_type] = url
            else:
                logger.warning(f"Alternative URL for {file_type} returned status code {response.status_code}")
        except Exception as e:
            logger.warning(f"Error checking alternative URL for {file_type}: {e}")
    
    if valid_urls:
        logger.info(f"Found {len(valid_urls)} valid alternative URLs for year {year}")
        return valid_urls
    else:
        logger.warning(f"No valid alternative URLs found for year {year}")
        return None

def download_file(url, destination):
    """
    Download a file from a URL to a destination with progress bar.
    """
    try:
        # If the URL is a local file path, copy it instead of downloading
        if os.path.isfile(url):
            import shutil
            shutil.copy2(url, destination)
            logger.info(f"Copied local file {url} to {destination}")
            return True
            
        # Download from URL
        response = requests.get(url, stream=True, timeout=30)
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

def setup_download_folder(year):
    """Set up the download folder structure for the specified year."""
    data_dir = Path(__file__).parent.parent / "data"
    data_dir.mkdir(exist_ok=True)
    
    year_dir = data_dir / str(year)
    year_dir.mkdir(exist_ok=True)
    
    return year_dir

def main():
    """
    Main function to download PLS data.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Download PLS data for a specific year")
    parser.add_argument("--year", type=str, default="2021", help="Year to download data for (default: 2021)")
    parser.add_argument("--force", action="store_true", help="Force download even if files already exist")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Set logging level based on verbose flag
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    year = args.year
    logger.info(f"Starting download process for PLS data for year {year}")
    
    # Set up download folder
    year_dir = setup_download_folder(year)
    
    # Try different methods to find the URLs
    urls = find_pls_data_urls_from_imls(year)
    
    if not urls:
        logger.warning("Could not find URLs from IMLS website, trying alternative URLs")
        urls = try_alternative_download_urls(year)
    
    if not urls:
        logger.warning("Could not find URLs from alternative sources, trying Data.gov API")
        urls = get_data_from_datagov_api(year)
    
    if not urls:
        logger.error(f"All methods to find PLS data URLs for year {year} failed")
        sys.exit(1)
    
    # Download files
    download_success = False
    for file_type, url in urls.items():
        file_name = f"pls_{year}_{file_type}.csv"
        destination = year_dir / file_name
        
        if destination.exists() and not args.force:
            logger.info(f"File {destination} already exists. Use --force to overwrite.")
            download_success = True
            continue
            
        success = download_file(url, destination)
        if success:
            download_success = True
        else:
            logger.error(f"Failed to download {file_name}")
    
    if download_success:
        logger.info(f"Download process completed for year {year}")
        
        # Create a metadata file with information about the download
        metadata = {
            "year": year,
            "download_date": time.strftime("%Y-%m-%d %H:%M:%S"),
            "files": [f.name for f in year_dir.glob(f"pls_{year}_*.csv")],
            "source": "IMLS website" if "imls.gov" in next(iter(urls.values())) else "Alternative source"
        }
        
        with open(year_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
    else:
        logger.error(f"Failed to download any files for year {year}")
        sys.exit(1)

if __name__ == "__main__":
    main() 