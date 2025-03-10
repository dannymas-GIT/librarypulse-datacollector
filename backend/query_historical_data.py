"""
Script to query historical data for West Babylon Public Library.
This script provides functions to query the historical data table,
generate trend analysis, and export data to JSON.
"""
import argparse
import json
import logging
import os
import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import psycopg2
from psycopg2.extras import RealDictCursor

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("query_historical.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Constants
WEST_BABYLON_ID = "NY0773"
EXPORT_DIR = Path("data/exports")
DB_PARAMS = {
    "dbname": "librarypulse",
    "user": "postgres",
    "password": "postgres",
    "host": "localhost",
    "port": "5432"
}

def ensure_dirs():
    """Ensure export directory exists."""
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    return True

def get_db_connection():
    """Create a database connection."""
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        conn.autocommit = False
        return conn
    except psycopg2.Error as e:
        logger.error(f"Error connecting to database: {e}")
        return None

def get_available_years(conn, library_id=WEST_BABYLON_ID):
    """Get a list of available years for the library."""
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "SELECT year FROM library_historical_data WHERE library_id = %s ORDER BY year",
            (library_id,)
        )
        years = [row[0] for row in cursor.fetchall()]
        return years
    except psycopg2.Error as e:
        logger.error(f"Error getting available years: {e}")
        return []
    finally:
        cursor.close()

def get_library_data_for_year(conn, year, library_id=WEST_BABYLON_ID):
    """Get library data for a specific year."""
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute(
            "SELECT * FROM library_historical_data WHERE library_id = %s AND year = %s",
            (library_id, year)
        )
        data = cursor.fetchone()
        return dict(data) if data else None
    except psycopg2.Error as e:
        logger.error(f"Error getting library data for year {year}: {e}")
        return None
    finally:
        cursor.close()

def get_all_library_data(conn, library_id=WEST_BABYLON_ID):
    """Get all historical data for the library."""
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cursor.execute(
            "SELECT * FROM library_historical_data WHERE library_id = %s ORDER BY year",
            (library_id,)
        )
        data = cursor.fetchall()
        return [dict(row) for row in data]
    except psycopg2.Error as e:
        logger.error(f"Error getting all library data: {e}")
        return []
    finally:
        cursor.close()

def export_data_to_json(data, filename):
    """Export data to a JSON file."""
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Data exported to {filename}")
        return True
    except Exception as e:
        logger.error(f"Error exporting data to {filename}: {e}")
        return False

def generate_trend_analysis(data, metrics, output_file=None):
    """
    Generate trend analysis for specified metrics.
    
    Args:
        data: List of library data dictionaries
        metrics: List of metrics to analyze
        output_file: Optional file to save the plot
    """
    if not data or not metrics:
        logger.error("No data or metrics provided for trend analysis")
        return False
    
    # Convert to DataFrame for easier analysis
    df = pd.DataFrame(data)
    
    # Set year as index
    if 'year' in df.columns:
        df.set_index('year', inplace=True)
    
    # Filter to only include requested metrics
    metrics_to_plot = [m for m in metrics if m in df.columns]
    
    if not metrics_to_plot:
        logger.error(f"None of the requested metrics {metrics} found in data")
        return False
    
    # Create the plot
    plt.figure(figsize=(12, 8))
    
    for metric in metrics_to_plot:
        plt.plot(df.index, df[metric], marker='o', label=metric)
    
    plt.title(f"West Babylon Public Library - Historical Trends")
    plt.xlabel("Year")
    plt.ylabel("Value")
    plt.legend()
    plt.grid(True)
    
    if output_file:
        plt.savefig(output_file)
        logger.info(f"Trend analysis saved to {output_file}")
    else:
        plt.show()
    
    return True

def calculate_growth_rates(data, metrics):
    """
    Calculate growth rates for specified metrics.
    
    Args:
        data: List of library data dictionaries
        metrics: List of metrics to analyze
        
    Returns:
        Dictionary with growth rates
    """
    if not data or not metrics:
        logger.error("No data or metrics provided for growth rate calculation")
        return {}
    
    # Convert to DataFrame for easier analysis
    df = pd.DataFrame(data)
    
    # Set year as index
    if 'year' in df.columns:
        df.set_index('year', inplace=True)
    
    # Filter to only include requested metrics
    metrics_to_analyze = [m for m in metrics if m in df.columns]
    
    if not metrics_to_analyze:
        logger.error(f"None of the requested metrics {metrics} found in data")
        return {}
    
    # Calculate growth rates
    results = {}
    
    for metric in metrics_to_analyze:
        # Skip if the metric has non-numeric values
        if not pd.api.types.is_numeric_dtype(df[metric]):
            continue
            
        # Calculate year-over-year growth rates
        growth_rates = df[metric].pct_change() * 100
        
        # Calculate average growth rate (excluding NaN values)
        avg_growth = growth_rates.mean()
        
        # Calculate total growth from first to last year
        first_value = df[metric].iloc[0]
        last_value = df[metric].iloc[-1]
        
        if first_value and first_value != 0:
            total_growth = ((last_value - first_value) / first_value) * 100
        else:
            total_growth = float('nan')
        
        results[metric] = {
            'average_annual_growth_rate': avg_growth,
            'total_growth_rate': total_growth,
            'first_year_value': first_value,
            'last_year_value': last_value,
            'yearly_growth_rates': growth_rates.to_dict()
        }
    
    return results

def print_library_summary(data):
    """Print a summary of the library data."""
    if not data:
        print("No data available")
        return
    
    # Get the most recent year's data
    recent_data = data[-1]
    
    print(f"\n=== West Babylon Public Library Summary ({recent_data['year']}) ===")
    print(f"Location: {recent_data['address']}, {recent_data['city']}, {recent_data['state']} {recent_data['zip_code']}")
    print(f"County: {recent_data['county']}")
    print(f"Phone: {recent_data['phone']}")
    print(f"\nService Area Population: {recent_data['service_area_population']:,}")
    
    print("\n--- Facilities ---")
    print(f"Central Libraries: {recent_data['central_library_count']}")
    print(f"Branch Libraries: {recent_data['branch_library_count']}")
    print(f"Bookmobiles: {recent_data['bookmobile_count']}")
    
    print("\n--- Collections ---")
    print(f"Print Materials: {recent_data['print_collection']:,}")
    print(f"Electronic Materials: {recent_data['electronic_collection']:,}")
    print(f"Audio Materials: {recent_data['audio_collection']:,}")
    print(f"Video Materials: {recent_data['video_collection']:,}")
    
    print("\n--- Usage ---")
    print(f"Total Circulation: {recent_data['total_circulation']:,}")
    if recent_data['electronic_circulation'] is not None:
        print(f"Electronic Circulation: {recent_data['electronic_circulation']:,}")
    if recent_data['physical_circulation'] is not None:
        print(f"Physical Circulation: {recent_data['physical_circulation']:,}")
    print(f"Annual Visits: {recent_data['visits']:,}")
    if recent_data['reference_transactions'] is not None:
        print(f"Reference Transactions: {recent_data['reference_transactions']:,}")
    if recent_data['registered_users'] is not None:
        print(f"Registered Users: {recent_data['registered_users']:,}")
    if recent_data['public_internet_computers'] is not None:
        print(f"Public Internet Computers: {recent_data['public_internet_computers']:,}")
    if recent_data['public_wifi_sessions'] is not None:
        print(f"Public WiFi Sessions: {recent_data['public_wifi_sessions']:,}")
    if recent_data['website_visits'] is not None:
        print(f"Website Visits: {recent_data['website_visits']:,}")
    
    print("\n--- Programs ---")
    print(f"Total Programs: {recent_data['total_programs']:,}")
    print(f"Total Program Attendance: {recent_data['total_program_attendance']:,}")
    if recent_data['children_programs'] is not None:
        print(f"Children's Programs: {recent_data['children_programs']:,}")
    if recent_data['children_program_attendance'] is not None:
        print(f"Children's Program Attendance: {recent_data['children_program_attendance']:,}")
    if recent_data['ya_programs'] is not None:
        print(f"Young Adult Programs: {recent_data['ya_programs']:,}")
    if recent_data['ya_program_attendance'] is not None:
        print(f"Young Adult Program Attendance: {recent_data['ya_program_attendance']:,}")
    if recent_data['adult_programs'] is not None:
        print(f"Adult Programs: {recent_data['adult_programs']:,}")
    if recent_data['adult_program_attendance'] is not None:
        print(f"Adult Program Attendance: {recent_data['adult_program_attendance']:,}")
    
    print("\n--- Staffing ---")
    print(f"Total Staff (FTE): {recent_data['total_staff']}")
    print(f"Librarians (FTE): {recent_data['librarian_staff']}")
    if recent_data['mls_librarian_staff'] is not None:
        print(f"MLS Librarians (FTE): {recent_data['mls_librarian_staff']}")
    if recent_data['other_staff'] is not None:
        print(f"Other Staff (FTE): {recent_data['other_staff']}")
    
    print("\n--- Financials ---")
    print(f"Total Operating Revenue: ${recent_data['total_operating_revenue']:,.2f}")
    if recent_data['local_operating_revenue'] is not None:
        print(f"Local Revenue: ${recent_data['local_operating_revenue']:,.2f}")
    if recent_data['state_operating_revenue'] is not None:
        print(f"State Revenue: ${recent_data['state_operating_revenue']:,.2f}")
    if recent_data['federal_operating_revenue'] is not None:
        print(f"Federal Revenue: ${recent_data['federal_operating_revenue']:,.2f}")
    if recent_data['other_operating_revenue'] is not None:
        print(f"Other Revenue: ${recent_data['other_operating_revenue']:,.2f}")
    print(f"Total Operating Expenditures: ${recent_data['total_operating_expenditures']:,.2f}")
    if recent_data['staff_expenditures'] is not None:
        print(f"Staff Expenditures: ${recent_data['staff_expenditures']:,.2f}")
    if recent_data['collection_expenditures'] is not None:
        print(f"Collection Expenditures: ${recent_data['collection_expenditures']:,.2f}")
    
    print("\n--- Historical Data Available ---")
    print(f"Years of data: {data[0]['year']} to {data[-1]['year']} ({len(data)} years)")

def print_trend_summary(data, metrics=None):
    """Print a summary of trends for the library data."""
    if not data:
        print("No data available for trend analysis")
        return
    
    # If no metrics specified, use a default set
    if not metrics:
        metrics = [
            'service_area_population',
            'print_collection',
            'electronic_collection',
            'total_circulation',
            'visits',
            'total_programs',
            'total_program_attendance',
            'total_staff',
            'total_operating_revenue',
            'total_operating_expenditures'
        ]
    
    # Calculate growth rates
    growth_rates = calculate_growth_rates(data, metrics)
    
    if not growth_rates:
        print("No growth rate data available")
        return
    
    print(f"\n=== West Babylon Public Library Trend Analysis ({data[0]['year']} to {data[-1]['year']}) ===")
    
    for metric, rates in growth_rates.items():
        print(f"\n--- {metric} ---")
        print(f"Value in {data[0]['year']}: {rates['first_year_value']:,}")
        print(f"Value in {data[-1]['year']}: {rates['last_year_value']:,}")
        print(f"Total growth: {rates['total_growth_rate']:.2f}%")
        print(f"Average annual growth: {rates['average_annual_growth_rate']:.2f}%")
        
        # Print notable years (highest growth and decline)
        yearly_rates = rates['yearly_growth_rates']
        if yearly_rates:
            # Filter out NaN values
            valid_rates = {k: v for k, v in yearly_rates.items() if not pd.isna(v)}
            
            if valid_rates:
                max_year = max(valid_rates, key=valid_rates.get)
                min_year = min(valid_rates, key=valid_rates.get)
                
                print(f"Highest growth: {valid_rates[max_year]:.2f}% in {max_year}")
                print(f"Largest decline: {valid_rates[min_year]:.2f}% in {min_year}")

def main():
    """Main function for querying historical library data."""
    parser = argparse.ArgumentParser(description='Query historical data for West Babylon Public Library')
    parser.add_argument('--year', type=int, help='Specific year to query')
    parser.add_argument('--export', type=str, help='Export data to JSON file')
    parser.add_argument('--trends', action='store_true', help='Show trend analysis')
    parser.add_argument('--metrics', type=str, nargs='+', help='Metrics to analyze in trend analysis')
    parser.add_argument('--plot', type=str, help='Generate and save trend plot to file')
    parser.add_argument('--summary', action='store_true', help='Show library summary')
    
    args = parser.parse_args()
    
    # Ensure export directory exists
    ensure_dirs()
    
    # Create database connection
    conn = get_db_connection()
    if not conn:
        logger.error("Failed to connect to database")
        return
    
    try:
        # Get available years
        years = get_available_years(conn)
        if not years:
            logger.error("No historical data available")
            return
        
        logger.info(f"Found historical data for years: {years[0]} to {years[-1]}")
        
        # Get data based on arguments
        if args.year:
            if args.year not in years:
                logger.error(f"No data available for year {args.year}")
                return
            
            data = [get_library_data_for_year(conn, args.year)]
            logger.info(f"Retrieved data for year {args.year}")
        else:
            data = get_all_library_data(conn)
            logger.info(f"Retrieved data for all {len(data)} years")
        
        # Export data if requested
        if args.export:
            export_path = EXPORT_DIR / args.export
            export_data_to_json(data, export_path)
        
        # Show trend analysis if requested
        if args.trends:
            print_trend_summary(data, args.metrics)
        
        # Generate plot if requested
        if args.plot:
            plot_path = EXPORT_DIR / args.plot
            generate_trend_analysis(data, args.metrics or ['visits', 'total_circulation', 'electronic_collection'], plot_path)
        
        # Show summary if requested or if no other options specified
        if args.summary or (not args.year and not args.export and not args.trends and not args.plot):
            print_library_summary(data)
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main() 