#!/usr/bin/env python3
"""
Script to download a sample PLS dataset.
"""
import os
import sys
import requests
import logging
from pathlib import Path
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Sample data URLs - these are direct links to PLS datasets
SAMPLE_DATA_URLS = {
    # Sample library data from 2020
    "library": "https://raw.githubusercontent.com/IMLS/public-libraries-survey/main/data/fy2020_pls_data_files/pls_fy2020_library_pud21i.csv",
    # Sample outlet data from 2020
    "outlet": "https://raw.githubusercontent.com/IMLS/public-libraries-survey/main/data/fy2020_pls_data_files/pls_fy2020_outlet_pud21i.csv",
}

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
    Main function to download sample PLS data.
    """
    # Create data directory if it doesn't exist
    data_dir = Path(__file__).parent.parent / "data" / "sample"
    data_dir.mkdir(exist_ok=True, parents=True)
    
    # Download sample files
    for file_type, url in SAMPLE_DATA_URLS.items():
        file_name = f"pls_sample_{file_type}.csv"
        destination = data_dir / file_name
        
        if destination.exists():
            logger.info(f"File {destination} already exists. Skipping download.")
            continue
            
        success = download_file(url, destination)
        if not success:
            logger.error(f"Failed to download {file_name}")
    
    logger.info("Sample data download completed")

if __name__ == "__main__":
    main() 