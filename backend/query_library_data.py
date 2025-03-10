"""
Script to query and display library data from the database.
"""
import argparse
import logging
import json
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from init_db_simple import PLSDataset, Library, LibraryOutlet, LibraryConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/librarypulse"

def get_all_libraries():
    """
    Get a list of all libraries in the database.
    """
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Query for all distinct libraries
        libraries = session.query(
            Library.library_id,
            Library.name,
            Library.city,
            Library.state
        ).distinct().all()
        
        logger.info(f"Found {len(libraries)} libraries in the database")
        
        for lib in libraries:
            logger.info(f"  - {lib.name} ({lib.library_id}) in {lib.city}, {lib.state}")
        
        return libraries
    
    except Exception as e:
        logger.error(f"Error querying libraries: {e}", exc_info=True)
        return []
    finally:
        session.close()

def get_available_years():
    """
    Get a list of all years with available data.
    """
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Query for all years with data
        years = session.query(PLSDataset.year).distinct().order_by(PLSDataset.year.desc()).all()
        years = [y[0] for y in years]
        
        logger.info(f"Found data for {len(years)} years: {', '.join(map(str, years))}")
        
        return years
    
    except Exception as e:
        logger.error(f"Error querying years: {e}", exc_info=True)
        return []
    finally:
        session.close()

def get_library_info(library_id, year=None):
    """
    Get detailed information for a specific library, optionally for a specific year.
    """
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Start with a query for the library
        query = session.query(Library).filter(Library.library_id == library_id)
        
        # If year is specified, filter by year
        if year:
            query = query.join(PLSDataset).filter(PLSDataset.year == year)
        
        # Get the results
        libraries = query.all()
        
        if not libraries:
            logger.error(f"No data found for library {library_id}")
            return None
        
        # Get the most recent library if no year was specified
        library = libraries[0] if year else max(libraries, key=lambda l: l.dataset.year)
        
        # Get outlets for this library
        outlets = session.query(LibraryOutlet).filter(
            LibraryOutlet.library_id == library_id,
            LibraryOutlet.dataset_id == library.dataset_id
        ).all()
        
        # Get config if it exists
        config = session.query(LibraryConfig).filter(
            LibraryConfig.library_id == library_id
        ).first()
        
        # Display library information
        logger.info("\n" + "="*50)
        logger.info(f"LIBRARY INFORMATION: {library.name}")
        logger.info("="*50)
        logger.info(f"ID: {library.library_id}")
        logger.info(f"Year: {library.dataset.year}")
        logger.info(f"Location: {library.address}, {library.city}, {library.state} {library.zip_code}")
        logger.info(f"County: {library.county}")
        logger.info(f"Phone: {library.phone}")
        logger.info(f"Service Area Population: {library.service_area_population:,}")
        
        logger.info("\nFACILITIES:")
        logger.info(f"Central Libraries: {library.central_library_count}")
        logger.info(f"Branch Libraries: {library.branch_library_count}")
        logger.info(f"Bookmobiles: {library.bookmobile_count or 0}")
        
        logger.info("\nUSAGE STATISTICS:")
        logger.info(f"Annual Visits: {library.visits:,}")
        logger.info(f"Total Circulation: {library.total_circulation:,}")
        if library.electronic_circulation:
            logger.info(f"Electronic Circulation: {library.electronic_circulation:,}")
        if library.reference_transactions:
            logger.info(f"Reference Transactions: {library.reference_transactions:,}")
        if library.registered_users:
            logger.info(f"Registered Users: {library.registered_users:,}")
        
        logger.info("\nCOLLECTION:")
        logger.info(f"Print Materials: {library.print_collection:,}")
        logger.info(f"Electronic Materials: {library.electronic_collection:,}")
        logger.info(f"Audio Materials: {library.audio_collection:,}")
        logger.info(f"Video Materials: {library.video_collection:,}")
        
        logger.info("\nPROGRAMS:")
        if library.total_programs:
            logger.info(f"Total Programs: {library.total_programs:,}")
        if library.total_program_attendance:
            logger.info(f"Total Program Attendance: {library.total_program_attendance:,}")
        
        logger.info("\nSTAFFING:")
        logger.info(f"Total Staff (FTE): {library.total_staff}")
        if library.librarian_staff:
            logger.info(f"Librarians (FTE): {library.librarian_staff}")
        
        logger.info("\nFINANCIAL:")
        logger.info(f"Total Operating Revenue: ${library.total_operating_revenue:,.2f}")
        logger.info(f"Total Operating Expenditures: ${library.total_operating_expenditures:,.2f}")
        if library.staff_expenditures:
            logger.info(f"Staff Expenditures: ${library.staff_expenditures:,.2f}")
        if library.collection_expenditures:
            logger.info(f"Collection Expenditures: ${library.collection_expenditures:,.2f}")
        
        if outlets:
            logger.info("\nOUTLETS:")
            for outlet in outlets:
                logger.info(f"  - {outlet.name} ({outlet.outlet_id})")
                logger.info(f"    Type: {outlet.type}")
                logger.info(f"    Address: {outlet.address}, {outlet.city}, {outlet.state} {outlet.zip_code}")
                logger.info(f"    Square Feet: {outlet.square_feet:,}")
                logger.info(f"    Weekly Hours: {outlet.hours}")
                
        if config:
            logger.info("\nCONFIGURATION:")
            logger.info(f"Active: {'Yes' if config.is_active else 'No'}")
        
        # Return a dictionary with the library information
        result = {
            'library_id': library.library_id,
            'name': library.name,
            'year': library.dataset.year,
            'location': {
                'address': library.address,
                'city': library.city,
                'state': library.state,
                'zip_code': library.zip_code,
                'county': library.county
            },
            'service_area_population': library.service_area_population,
            'facilities': {
                'central_libraries': library.central_library_count,
                'branch_libraries': library.branch_library_count,
                'bookmobiles': library.bookmobile_count
            },
            'usage': {
                'visits': library.visits,
                'total_circulation': library.total_circulation,
                'electronic_circulation': library.electronic_circulation,
                'reference_transactions': library.reference_transactions,
                'registered_users': library.registered_users
            },
            'collection': {
                'print_materials': library.print_collection,
                'electronic_materials': library.electronic_collection,
                'audio_materials': library.audio_collection,
                'video_materials': library.video_collection
            },
            'programs': {
                'total_programs': library.total_programs,
                'total_attendance': library.total_program_attendance
            },
            'staff': {
                'total_staff': library.total_staff,
                'librarians': library.librarian_staff
            },
            'financial': {
                'total_revenue': library.total_operating_revenue,
                'total_expenditures': library.total_operating_expenditures,
                'staff_expenditures': library.staff_expenditures,
                'collection_expenditures': library.collection_expenditures
            },
            'outlets': [{
                'outlet_id': o.outlet_id,
                'name': o.name,
                'type': o.type,
                'address': o.address,
                'city': o.city,
                'state': o.state,
                'zip_code': o.zip_code,
                'square_feet': o.square_feet,
                'hours': o.hours
            } for o in outlets]
        }
        
        return result
    
    except Exception as e:
        logger.error(f"Error getting library info: {e}", exc_info=True)
        return None
    finally:
        session.close()

def get_library_comparison(library_ids, year=None):
    """
    Compare multiple libraries side by side, optionally for a specific year.
    """
    results = {}
    
    for library_id in library_ids:
        results[library_id] = get_library_info(library_id, year)
        
    # Now display a comparison table
    if results:
        logger.info("\n" + "="*100)
        logger.info("LIBRARY COMPARISON")
        logger.info("="*100)
        
        # Get column widths
        names = [r['name'] if r else "Unknown" for r in results.values()]
        col_width = max(20, max(len(name) for name in names) + 2)
        
        # Header
        header = "Metric".ljust(30) + "".join(name.ljust(col_width) for name in names)
        logger.info(header)
        logger.info("-" * len(header))
        
        # Service population
        row = "Service Population".ljust(30)
        for r in results.values():
            if r and r['service_area_population']:
                row += f"{r['service_area_population']:,}".ljust(col_width)
            else:
                row += "N/A".ljust(col_width)
        logger.info(row)
        
        # Visits
        row = "Annual Visits".ljust(30)
        for r in results.values():
            if r and r['usage']['visits']:
                row += f"{r['usage']['visits']:,}".ljust(col_width)
            else:
                row += "N/A".ljust(col_width)
        logger.info(row)
        
        # Circulation
        row = "Total Circulation".ljust(30)
        for r in results.values():
            if r and r['usage']['total_circulation']:
                row += f"{r['usage']['total_circulation']:,}".ljust(col_width)
            else:
                row += "N/A".ljust(col_width)
        logger.info(row)
        
        # Collection
        row = "Collection Size".ljust(30)
        for r in results.values():
            if r and r['collection']['print_materials']:
                row += f"{r['collection']['print_materials']:,}".ljust(col_width)
            else:
                row += "N/A".ljust(col_width)
        logger.info(row)
        
        # Staff
        row = "Total Staff (FTE)".ljust(30)
        for r in results.values():
            if r and r['staff']['total_staff']:
                row += f"{r['staff']['total_staff']}".ljust(col_width)
            else:
                row += "N/A".ljust(col_width)
        logger.info(row)
        
        # Revenue
        row = "Operating Revenue".ljust(30)
        for r in results.values():
            if r and r['financial']['total_revenue']:
                row += f"${r['financial']['total_revenue']:,.2f}".ljust(col_width)
            else:
                row += "N/A".ljust(col_width)
        logger.info(row)
        
        # Expenditures
        row = "Operating Expenditures".ljust(30)
        for r in results.values():
            if r and r['financial']['total_expenditures']:
                row += f"${r['financial']['total_expenditures']:,.2f}".ljust(col_width)
            else:
                row += "N/A".ljust(col_width)
        logger.info(row)
        
        # Programs
        row = "Total Programs".ljust(30)
        for r in results.values():
            if r and r['programs']['total_programs']:
                row += f"{r['programs']['total_programs']:,}".ljust(col_width)
            else:
                row += "N/A".ljust(col_width)
        logger.info(row)
    
    return results

def export_to_json(data, output_file):
    """
    Export data to a JSON file.
    """
    try:
        # Convert non-serializable objects to strings
        def json_serializer(obj):
            if isinstance(obj, (set, frozenset)):
                return list(obj)
            return str(obj)
        
        with open(output_file, 'w') as f:
            json.dump(data, f, default=json_serializer, indent=2)
            
        logger.info(f"Data exported to {output_file}")
        return True
    except Exception as e:
        logger.error(f"Error exporting data: {e}", exc_info=True)
        return False

def main():
    """
    Main function to handle command line arguments.
    """
    parser = argparse.ArgumentParser(description='Query library data from the database.')
    parser.add_argument('--list', action='store_true', help='List all libraries')
    parser.add_argument('--years', action='store_true', help='List all available years')
    parser.add_argument('--library', help='Library ID to query')
    parser.add_argument('--year', type=int, help='Year to query')
    parser.add_argument('--compare', nargs='+', help='Library IDs to compare')
    parser.add_argument('--export', help='Export data to JSON file')
    
    args = parser.parse_args()
    
    if args.list:
        libraries = get_all_libraries()
        
        if args.export and libraries:
            library_list = [{'library_id': l.library_id, 'name': l.name, 'city': l.city, 'state': l.state} 
                           for l in libraries]
            export_to_json(library_list, args.export)
        
    elif args.years:
        years = get_available_years()
        
        if args.export and years:
            export_to_json({'years': years}, args.export)
        
    elif args.library:
        library_info = get_library_info(args.library, args.year)
        
        if args.export and library_info:
            export_to_json(library_info, args.export)
        
    elif args.compare:
        results = get_library_comparison(args.compare, args.year)
        
        if args.export and results:
            export_to_json(results, args.export)
            
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 