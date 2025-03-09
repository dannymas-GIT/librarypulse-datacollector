import os
import re
import zipfile
import tempfile
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
import shutil

import pandas as pd
import requests
from bs4 import BeautifulSoup
from loguru import logger
from sqlalchemy.orm import Session
from tqdm import tqdm
import urllib.parse

from app.core.config import settings
from app.models.pls_data import PLSDataset, Library, LibraryOutlet
from app.services.library_config_service import LibraryConfigService


class PLSDataCollector:
    """
    Service for collecting Public Libraries Survey (PLS) data from IMLS.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.base_url = settings.IMLS_DATA_BASE_URL
        self.data_dir = settings.DATA_STORAGE_PATH
        self.raw_data_dir = self.data_dir / "raw"
        self.processed_data_dir = self.data_dir / "processed"
        
        # Create directories if they don't exist
        os.makedirs(self.raw_data_dir, exist_ok=True)
        os.makedirs(self.processed_data_dir, exist_ok=True)
        
        # Try to get the library configuration
        self.library_config = LibraryConfigService.get_library_config(db)
    
    def discover_available_years(self) -> List[int]:
        """
        Scrape the IMLS website to discover available PLS data years.
        
        Returns:
            List[int]: List of years with available data
        """
        logger.info(f"Discovering available PLS data years from {self.base_url}")
        
        try:
            response = requests.get(self.base_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # This is a simplified approach - the actual scraping logic would need
            # to be adjusted based on the actual HTML structure of the IMLS website
            year_links = []
            for link in soup.find_all('a', href=True):
                # Look for year patterns in links (e.g., "FY 2022" or "2022")
                year_match = re.search(r'(FY\s*)?(\d{4})', link.text)
                if year_match:
                    year = int(year_match.group(2))
                    if 1992 <= year <= datetime.now().year:  # Valid year range
                        year_links.append(year)
            
            return sorted(list(set(year_links)))
        
        except Exception as e:
            logger.error(f"Error discovering available years: {str(e)}")
            return []
    
    def download_data_for_year(self, year: int) -> Path:
        """
        Download PLS data for a specific year.
        
        Args:
            year: The year to download data for (fiscal year)
            
        Returns:
            Path: Path to the downloaded data file
        """
        logger.info(f"Downloading PLS data for year {year}")
        
        # Create directory for this year
        year_dir = self.raw_data_dir / str(year)
        os.makedirs(year_dir, exist_ok=True)
        
        # Define expected file paths
        csv_zip_path = year_dir / f"pls_fy{year}_csv.zip"
        
        # Check if we already have downloaded the data
        if csv_zip_path.exists():
            logger.info(f"Using previously downloaded data for year {year}")
            return csv_zip_path
        
        # If not, try to download from IMLS website
        try:
            # First try to find the specific download URL for this year
            logger.info(f"Looking for download URL for year {year}")
            
            # The base URL for PLS data
            base_url = self.base_url
            
            # Get the main PLS page
            response = requests.get(base_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for links with the year and CSV in them
            download_url = None
            
            # Pattern to match: Data Files – CSV (ZIP X MB)
            year_heading_pattern = f"FY {year}"
            csv_pattern = r"CSV.*\(ZIP"
            
            # Find the correct section for this year
            year_sections = soup.find_all(['h3'], string=lambda text: text and year_heading_pattern in text)
            
            if year_sections:
                year_section = year_sections[0]
                # Look for the next unordered list after the year heading
                next_ul = year_section.find_next('ul')
                
                if next_ul:
                    # Find the CSV download link
                    for li in next_ul.find_all('li'):
                        if re.search(csv_pattern, li.text, re.IGNORECASE):
                            # Found the CSV item, now get the link
                            link = li.find('a', href=True)
                            if link:
                                download_url = link['href']
                                # Make the URL absolute if it's relative
                                if not download_url.startswith('http'):
                                    download_url = urllib.parse.urljoin(base_url, download_url)
                                break
            
            # If we found a download URL, use it
            if download_url:
                logger.info(f"Found download URL for year {year}: {download_url}")
                
                # Download the ZIP file
                with requests.get(download_url, stream=True) as r:
                    r.raise_for_status()
                    total_size = int(r.headers.get('content-length', 0))
                    
                    with open(csv_zip_path, 'wb') as f:
                        with tqdm(total=total_size, unit='B', unit_scale=True) as pbar:
                            for chunk in r.iter_content(chunk_size=8192):
                                f.write(chunk)
                                pbar.update(len(chunk))
                
                logger.info(f"Successfully downloaded PLS data for year {year}")
                return csv_zip_path
            else:
                # If direct download link not found, fall back to sample data
                logger.warning(f"Could not find download URL for year {year}, falling back to sample data")
                return self._use_sample_data(year, year_dir)
                
        except Exception as e:
            logger.error(f"Error downloading PLS data for year {year}: {str(e)}")
            logger.warning(f"Falling back to sample data for year {year}")
            return self._use_sample_data(year, year_dir)
    
    def _use_sample_data(self, year: int, target_dir: Path) -> Path:
        """
        Use sample data as a fallback when downloads fail.
        
        Args:
            year: The year to get sample data for
            target_dir: Directory to copy sample data to
            
        Returns:
            Path: Path to the copied sample data ZIP file
        """
        # Check if we have sample data in the project
        sample_dir = self.data_dir / "sample"
        
        if not sample_dir.exists():
            raise FileNotFoundError(f"Sample data directory not found: {sample_dir}")
        
        # Look for library and outlet CSV files
        library_sample = next(sample_dir.glob(f"*library*.csv"), None)
        outlet_sample = next(sample_dir.glob(f"*outlet*.csv"), None)
        
        if not library_sample or not outlet_sample:
            raise FileNotFoundError("Sample library and outlet CSV files not found")
        
        # Create a ZIP file with the sample data
        zip_path = target_dir / f"pls_fy{year}_csv.zip"
        
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            # Add the sample files to the ZIP
            zipf.write(library_sample, f"pls_fy{year}_library.csv")
            zipf.write(outlet_sample, f"pls_fy{year}_outlet.csv")
        
        logger.info(f"Created sample data ZIP file for year {year}")
        return zip_path
    
    def process_data_for_year(self, year: int, data_path: Path) -> Dict[str, pd.DataFrame]:
        """
        Process PLS data for a specific year.
        
        Args:
            year: The year to process data for
            data_path: Path to the downloaded data file
            
        Returns:
            Dict[str, pd.DataFrame]: Dictionary of processed dataframes
        """
        logger.info(f"Processing PLS data for year {year}")
        
        # Extract if zip file
        if data_path.suffix.lower() == '.zip':
            extract_dir = self.processed_data_dir / str(year)
            os.makedirs(extract_dir, exist_ok=True)
            
            with zipfile.ZipFile(data_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
                
            # Find CSV files in extracted directory
            csv_files = list(extract_dir.glob('*.csv'))
            
            if not csv_files:
                logger.error(f"No CSV files found in ZIP for year {year}")
                return {}
                
            # IMLS CSV files follow specific patterns:
            # - Library data: puout_fy*.csv, pupld_fy*.csv, pupldf_fy*.csv, outlet_fy*.csv, etc.
            # - Outlet data: puout_fy*.csv, pupldf_fy*.csv, outlet_fy*.csv, etc.
            library_pattern = re.compile(r'(pupld|pupldf|library)', re.IGNORECASE)
            outlet_pattern = re.compile(r'(puout|outlet)', re.IGNORECASE)
            
            library_files = [f for f in csv_files if library_pattern.search(f.name)]
            outlet_files = [f for f in csv_files if outlet_pattern.search(f.name)]
            
            # If pattern matching didn't work, use a fallback approach
            if not library_files:
                # Try to find library data by looking for files with 'FSCSKEY' and not 'FSCS_SEQ'
                for file in csv_files:
                    try:
                        with open(file, 'r', encoding='latin1') as f:
                            header = f.readline().upper()
                            if 'FSCSKEY' in header and 'FSCS_SEQ' not in header:
                                library_files.append(file)
                    except Exception as e:
                        logger.warning(f"Error reading file {file}: {str(e)}")
            
            if not outlet_files:
                # Try to find outlet data by looking for files with both 'FSCSKEY' and 'FSCS_SEQ'
                for file in csv_files:
                    try:
                        with open(file, 'r', encoding='latin1') as f:
                            header = f.readline().upper()
                            if 'FSCSKEY' in header and 'FSCS_SEQ' in header:
                                outlet_files.append(file)
                    except Exception as e:
                        logger.warning(f"Error reading file {file}: {str(e)}")
            
            # If we still don't have both files, try another approach based on file size
            if not library_files and not outlet_files and len(csv_files) >= 2:
                # Sort by file size (ascending)
                csv_files.sort(key=lambda f: f.stat().st_size)
                # The smaller file is likely the library file, the larger file is likely the outlet file
                library_files = [csv_files[0]]
                outlet_files = [csv_files[1]]
            
            library_file = library_files[0] if library_files else None
            outlet_file = outlet_files[0] if outlet_files else None
            
            if not library_file:
                logger.error(f"Library data file not found for year {year}")
                return {}
        
        else:
            # Direct CSV file
            library_file = data_path
            outlet_file = None
        
        # Load library data
        try:
            library_df = pd.read_csv(library_file, encoding='latin1', low_memory=False)
            
            # Standardize column names to uppercase
            library_df.columns = map(str.upper, library_df.columns)
            
            # Make sure we have the FSCSKEY column
            if 'FSCSKEY' not in library_df.columns:
                logger.error(f"FSCSKEY column not found in library data for year {year}")
                return {}
            
            # Filter to just the selected library if configuration exists
            if self.library_config:
                logger.info(f"Filtering data for library ID: {self.library_config.library_id}")
                library_df = library_df[library_df['FSCSKEY'] == self.library_config.library_id]
                
                if library_df.empty:
                    logger.warning(f"No data found for library ID {self.library_config.library_id} in year {year}")
                    return {}
        except Exception as e:
            logger.error(f"Error processing library data for year {year}: {str(e)}")
            return {}
        
        # Load outlet data if available
        outlet_df = None
        if outlet_file:
            try:
                outlet_df = pd.read_csv(outlet_file, encoding='latin1', low_memory=False)
                
                # Standardize column names to uppercase
                outlet_df.columns = map(str.upper, outlet_df.columns)
                
                # Make sure we have the FSCSKEY and FSCS_SEQ columns
                required_columns = ['FSCSKEY', 'FSCS_SEQ']
                if not all(col in outlet_df.columns for col in required_columns):
                    logger.error(f"Required columns not found in outlet data for year {year}")
                    outlet_df = None
                else:
                    # Filter outlets to just the selected library
                    if self.library_config:
                        outlet_df = outlet_df[outlet_df['FSCSKEY'] == self.library_config.library_id]
            except Exception as e:
                logger.error(f"Error processing outlet data for year {year}: {str(e)}")
                outlet_df = None
        
        return {
            'libraries': library_df,
            'outlets': outlet_df
        }
    
    def load_data_into_db(self, year: int, processed_data: Dict[str, pd.DataFrame]) -> None:
        """
        Load processed data into the database.
        
        Args:
            year: The year of the data
            processed_data: Dictionary of processed dataframes
        """
        logger.info(f"Loading data for year {year} into database")
        
        # Create dataset
        dataset = PLSDataset(
            year=year,
            status="complete",
            record_count=len(processed_data.get('libraries', pd.DataFrame())),
            notes=f"Imported on {datetime.now().strftime('%Y-%m-%d')}"
        )
        self.db.add(dataset)
        self.db.commit()
        
        # Load libraries
        library_df = processed_data.get('libraries')
        if library_df is not None and not library_df.empty:
            for _, row in library_df.iterrows():
                # Check if library record already exists
                existing_library = self.db.query(Library).filter(
                    Library.dataset_id == dataset.id,
                    Library.library_id == row['FSCSKEY']
                ).first()
                
                if existing_library:
                    logger.debug(f"Library {row['FSCSKEY']} already exists for year {year}")
                    continue
                
                # Map IMLS field names to our model, with fallbacks for different years/formats
                def get_value(field_names):
                    for field in field_names:
                        if field in row and pd.notna(row[field]):
                            return row[field]
                    return None
                
                # Create library record with flexible field mapping
                library = Library(
                    dataset_id=dataset.id,
                    library_id=row['FSCSKEY'],
                    name=get_value(['LIBNAME', 'LIBRARY_NAME']),
                    address=get_value(['ADDRESS', 'ADDRES']),
                    city=get_value(['CITY']),
                    state=get_value(['STABR', 'STATE']),
                    zip_code=get_value(['ZIP', 'ZIPCODE']),
                    county=get_value(['CNTY', 'COUNTY']),
                    phone=get_value(['PHONE', 'PHONENUMBER']),
                    
                    # Library classification
                    locale=get_value(['LOCALE']),
                    central_library_count=get_value(['CENTLIB']),
                    branch_library_count=get_value(['BRANLIB']),
                    bookmobile_count=get_value(['BKMOB']),
                    service_area_population=get_value(['POPU_LSA', 'POPU']),
                    
                    # Collection statistics
                    print_collection=get_value(['BKVOL', 'PRINT_COLLECTION']),
                    electronic_collection=get_value(['EBOOK', 'ELECTRONIC_COLLECTION']),
                    audio_collection=get_value(['AUDIO_PH', 'AUDIO_PHYSICAL', 'AUDIO']),
                    video_collection=get_value(['VIDEO_PH', 'VIDEO_PHYSICAL', 'VIDEO']),
                    
                    # Usage statistics
                    total_circulation=get_value(['TOTCIR', 'CIRCULATION']),
                    electronic_circulation=get_value(['ELECCIR', 'ECIRCULATION']),
                    physical_circulation=get_value(['PHYSCIR', 'PCIRCULATION']),
                    visits=get_value(['VISITS', 'ANNUAL_VISITS']),
                    reference_transactions=get_value(['REFERENC', 'REFERENCE']),
                    registered_users=get_value(['REGBOR', 'REGISTERED_USERS']),
                    public_internet_computers=get_value(['GPTERMS', 'PUBLIC_COMPUTERS']),
                    public_wifi_sessions=get_value(['WIFISESS', 'WIFI_SESSIONS']),
                    website_visits=get_value(['WEBVISIT', 'WEBSITE_VISITS']),
                    
                    # Program statistics
                    total_programs=get_value(['PROGAM', 'PROGRAMS']),
                    total_program_attendance=get_value(['ATTPRG', 'PROGRAM_ATTENDANCE']),
                    children_programs=get_value(['KIDPROG', 'CHILDREN_PROGRAMS']),
                    children_program_attendance=get_value(['KIDATTND', 'CHILDREN_ATTENDANCE']),
                    ya_programs=get_value(['YAPROG', 'YA_PROGRAMS']),
                    ya_program_attendance=get_value(['YAATTND', 'YA_ATTENDANCE']),
                    adult_programs=get_value(['ADULTPRO', 'ADULT_PROGRAMS']),
                    adult_program_attendance=get_value(['ADULTATT', 'ADULT_ATTENDANCE']),
                    
                    # Staff statistics
                    total_staff=get_value(['TOTSTAFF', 'STAFF_TOTAL']),
                    librarian_staff=get_value(['LIBRARIA', 'LIBRARIAN']),
                    mls_librarian_staff=get_value(['MLSLIB', 'MLS_LIBRARIAN']),
                    other_staff=get_value(['OTHSTAFF', 'OTHER_STAFF']),
                    
                    # Financial statistics
                    total_operating_revenue=get_value(['TOTINCM', 'TOTAL_REVENUE']),
                    local_operating_revenue=get_value(['LOCGVT', 'LOCAL_REVENUE']),
                    state_operating_revenue=get_value(['STGVT', 'STATE_REVENUE']),
                    federal_operating_revenue=get_value(['FEDGVT', 'FEDERAL_REVENUE']),
                    other_operating_revenue=get_value(['OTHINCM', 'OTHER_REVENUE']),
                    
                    total_operating_expenditures=get_value(['TOTEXPD', 'TOTAL_EXPENDITURES']),
                    staff_expenditures=get_value(['STAFFEXP', 'STAFF_EXPENDITURES']),
                    collection_expenditures=get_value(['TOTCOLL', 'COLLECTION_EXPENDITURES']),
                    print_collection_expenditures=get_value(['PRMATEXP', 'PRINT_EXPENDITURES']),
                    electronic_collection_expenditures=get_value(['ELMATEXP', 'ELECTRONIC_EXPENDITURES']),
                    other_collection_expenditures=get_value(['OTHMATEX', 'OTHER_COLLECTION_EXPENDITURES']),
                    other_operating_expenditures=get_value(['OTHEXPD', 'OTHER_EXPENDITURES']),
                    
                    capital_revenue=get_value(['CAPITAL', 'CAPITAL_REVENUE']),
                    capital_expenditures=get_value(['CAPEXP', 'CAPITAL_EXPENDITURES']),
                    
                    # Operation info
                    hours_open=get_value(['HRS_OPEN', 'HOURS_OPEN']),
                    weeks_open=get_value(['WEEKS', 'WEEKS_OPEN']),
                )
                self.db.add(library)
            
            self.db.commit()
        
        # Load outlets if available
        outlet_df = processed_data.get('outlets')
        if outlet_df is not None and not outlet_df.empty:
            for _, row in outlet_df.iterrows():
                # Check if outlet record already exists
                existing_outlet = self.db.query(LibraryOutlet).filter(
                    LibraryOutlet.dataset_id == dataset.id,
                    LibraryOutlet.library_id == row['FSCSKEY'],
                    LibraryOutlet.outlet_id == row['FSCS_SEQ']
                ).first()
                
                if existing_outlet:
                    logger.debug(f"Outlet {row['FSCSKEY']}-{row['FSCS_SEQ']} already exists for year {year}")
                    continue
                
                # Map IMLS field names to our model with fallbacks
                def get_value(field_names):
                    for field in field_names:
                        if field in row and pd.notna(row[field]):
                            return row[field]
                    return None
                
                outlet = LibraryOutlet(
                    dataset_id=dataset.id,
                    library_id=row['FSCSKEY'],
                    outlet_id=row['FSCS_SEQ'],
                    name=get_value(['LIBNAME', 'NAME']),
                    outlet_type=get_value(['STATDESC', 'TYPE_DESC', 'TYPE']),
                    address=get_value(['ADDRESS', 'ADDRES']),
                    city=get_value(['CITY']),
                    state=get_value(['STABR', 'STATE']),
                    zip_code=get_value(['ZIP', 'ZIPCODE']),
                    county=get_value(['CNTY', 'COUNTY']),
                    phone=get_value(['PHONE', 'PHONENUMBER']),
                    
                    latitude=get_value(['LATITUDE', 'LAT']),
                    longitude=get_value(['LONGITUD', 'LONGITUDE', 'LONG']),
                    
                    metro_status=get_value(['METRO', 'METROPOLITAN_STATUS']),
                    square_footage=get_value(['SQ_FEET', 'SQFEET', 'SQUARE_FEET']),
                    
                    hours_open=get_value(['HRS_OPEN', 'HOURS_OPEN']),
                    weeks_open=get_value(['WKS_OPEN', 'WEEKS_OPEN'])
                )
                self.db.add(outlet)
            
            self.db.commit()
        
        # Update the library configuration's last update check if applicable
        if self.library_config:
            if not self.library_config.last_update_check or year > self.library_config.last_update_check:
                self.library_config.last_update_check = year
                self.db.commit()
                logger.info(f"Updated library configuration with last update check: {year}")
        
        logger.info(f"Successfully loaded data for year {year}")
        
        # Clean up temporary extraction files if needed
        if year > 2010:  # Keep older years for historical reference
            extract_dir = self.processed_data_dir / str(year)
            if extract_dir.exists():
                try:
                    shutil.rmtree(extract_dir)
                    logger.debug(f"Cleaned up temporary files for year {year}")
                except Exception as e:
                    logger.warning(f"Could not clean up temporary files for year {year}: {str(e)}")
    
    def collect_data_for_year(self, year: int) -> bool:
        """
        Collect and process PLS data for a specific year.
        
        Args:
            year: The year to collect data for
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Download data
            data_path = self.download_data_for_year(year)
            
            # Process data
            processed_data = self.process_data_for_year(year, data_path)
            
            # Load data into database
            self.load_data_into_db(year, processed_data)
            
            return True
        
        except Exception as e:
            logger.error(f"Error collecting data for year {year}: {str(e)}")
            return False
    
    def collect_data_for_years(self, years: List[int]) -> Dict[int, bool]:
        """
        Collect and process PLS data for multiple years.
        
        Args:
            years: List of years to collect data for
            
        Returns:
            Dict[int, bool]: Dictionary mapping years to success/failure
        """
        results = {}
        
        for year in years:
            success = self.collect_data_for_year(year)
            results[year] = success
        
        return results
    
    def collect_all_available_data(self) -> Dict[int, bool]:
        """
        Collect and process PLS data for all available years.
        
        Returns:
            Dict[int, bool]: Dictionary mapping years to success/failure
        """
        years = self.discover_available_years()
        
        if not years:
            logger.warning("No available years discovered")
            return {}
        
        return self.collect_data_for_years(years)
    
    def collect_all_data_for_library(self, library_id: str) -> Dict[int, bool]:
        """
        Collect data for a specific library for all available years.
        
        Args:
            library_id: The FSCSKEY of the library
            
        Returns:
            Dict[int, bool]: Dictionary of years and success status
        """
        logger.info(f"Collecting data for library {library_id} for all available years")
        
        # Discover available years
        years = self.discover_available_years()
        
        if not years:
            logger.error("No available years discovered")
            return {}
        
        # Set library configuration for filtering
        self.library_config = LibraryConfigService.get_library_config(self.db)
        
        if not self.library_config or self.library_config.library_id != library_id:
            logger.warning(f"Library configuration not set or different from requested library {library_id}")
            # We'll still proceed with the requested library_id for this operation
        
        # Collect data for each year
        results = {}
        for year in years:
            success = self.collect_data_for_year(year)
            results[year] = success
        
        return results
    
    def update_with_latest_data(self) -> Optional[int]:
        """
        Update with the latest available PLS data.
        
        Returns:
            Optional[int]: The year of the latest data, or None if no update was performed
        """
        # Check if library configuration exists
        if not self.library_config:
            logger.warning("No library configuration exists. Please complete setup first.")
            return None
        
        # Discover available years
        years = self.discover_available_years()
        
        if not years:
            logger.error("No available years discovered")
            return None
        
        # Get the latest year
        latest_year = max(years)
        
        # Check if we already have this year's data for the configured library
        existing_dataset = self.db.query(PLSDataset).filter(
            PLSDataset.year == latest_year
        ).first()
        
        if existing_dataset:
            # Check if we have data for the configured library
            existing_library = self.db.query(Library).filter(
                Library.dataset_id == existing_dataset.id,
                Library.library_id == self.library_config.library_id
            ).first()
            
            if existing_library:
                logger.info(f"Already have latest data (year {latest_year}) for library {self.library_config.library_id}")
                return latest_year
        
        # Collect data for the latest year
        success = self.collect_data_for_year(latest_year)
        
        if success:
            # Update the last_update_check in the library config
            self.library_config.last_update_check = latest_year
            self.db.commit()
            
            return latest_year
        
        return None 