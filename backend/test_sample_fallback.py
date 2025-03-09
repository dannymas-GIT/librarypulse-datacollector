import os
import sys
from pathlib import Path
import zipfile
import shutil
from loguru import logger

# Set up logging
logger.remove()
logger.add(sys.stderr, level="INFO")
logger.add("fallback_test.log", level="DEBUG", rotation="10 MB")

# Sample data paths
SAMPLE_DATA_DIR = Path("data/sample")
TARGET_DIR = Path("data/test_output")

def use_sample_data(year: int, target_dir: Path) -> Path:
    """
    Use sample data as a fallback when downloads fail.
    
    Args:
        year: The year to get sample data for
        target_dir: Directory to copy sample data to
        
    Returns:
        Path: Path to the copied sample data ZIP file
    """
    # Check if we have sample data in the project
    sample_dir = SAMPLE_DATA_DIR
    
    if not sample_dir.exists():
        raise FileNotFoundError(f"Sample data directory not found: {sample_dir}")
    
    # Look for library and outlet CSV files
    library_sample = next(sample_dir.glob(f"*library*.csv"), None)
    outlet_sample = next(sample_dir.glob(f"*outlet*.csv"), None)
    
    if not library_sample or not outlet_sample:
        raise FileNotFoundError("Sample library and outlet CSV files not found")
    
    # Create the target directory if it doesn't exist
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a ZIP file with the sample data
    zip_path = target_dir / f"pls_fy{year}_csv.zip"
    
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        # Add the sample files to the ZIP
        zipf.write(library_sample, f"pls_fy{year}_library.csv")
        zipf.write(outlet_sample, f"pls_fy{year}_outlet.csv")
    
    logger.info(f"Created sample data ZIP file for year {year} at {zip_path}")
    return zip_path


def extract_and_verify_zip(zip_path: Path, extract_dir: Path) -> bool:
    """Extract and verify the contents of a ZIP file."""
    try:
        # Clear extract directory if it exists
        if extract_dir.exists():
            shutil.rmtree(extract_dir)
        
        extract_dir.mkdir(parents=True, exist_ok=True)
        
        # Extract the ZIP file
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(extract_dir)
            logger.info(f"Extracted {len(zipf.namelist())} files from {zip_path} to {extract_dir}")
            
            # List the extracted files
            for file in zipf.namelist():
                logger.info(f"  - {file}")
        
        # Verify that files were extracted
        csv_files = list(extract_dir.glob("*.csv"))
        if not csv_files:
            logger.error("No CSV files found in extracted directory")
            return False
        
        return True
    
    except Exception as e:
        logger.error(f"Error extracting or verifying ZIP: {str(e)}")
        return False


if __name__ == "__main__":
    print("Testing sample data fallback mechanism...")
    
    # Clean up previous test outputs
    if TARGET_DIR.exists():
        shutil.rmtree(TARGET_DIR)
    
    try:
        # Test for current year
        current_year = 2023
        zip_path = use_sample_data(current_year, TARGET_DIR)
        
        if zip_path.exists():
            print(f"✅ Successfully created sample data ZIP for year {current_year}")
            
            # Verify ZIP contents
            extract_dir = TARGET_DIR / "extracted"
            if extract_and_verify_zip(zip_path, extract_dir):
                print(f"✅ Successfully extracted and verified ZIP contents")
            else:
                print(f"❌ Failed to extract or verify ZIP contents")
        else:
            print(f"❌ Failed to create sample data ZIP")
    
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
    
    print("\nFinished testing.") 