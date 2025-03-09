from typing import Dict, List, Optional, Any, Union
import json

from sqlalchemy.orm import Session

from app.models.library_config import LibraryConfig
from app.models.pls_data import Library


class LibraryConfigService:
    """
    Service for managing library configuration settings.
    """
    
    @staticmethod
    def get_library_config(db: Session) -> Optional[LibraryConfig]:
        """
        Get the library configuration or None if not set up.
        
        Args:
            db: Database session
            
        Returns:
            LibraryConfig or None
        """
        return db.query(LibraryConfig).first()
    
    @staticmethod
    def is_setup_complete(db: Session) -> bool:
        """
        Check if initial setup is complete.
        
        Args:
            db: Database session
            
        Returns:
            bool: True if setup is complete, False otherwise
        """
        config = LibraryConfigService.get_library_config(db)
        return config is not None and config.setup_complete
    
    @staticmethod
    def create_or_update_config(
        db: Session,
        library_id: str,
        library_name: str,
        collection_stats_enabled: bool = True,
        usage_stats_enabled: bool = True,
        program_stats_enabled: bool = True,
        staff_stats_enabled: bool = True,
        financial_stats_enabled: bool = True,
        collection_metrics: Optional[Dict[str, bool]] = None,
        usage_metrics: Optional[Dict[str, bool]] = None,
        program_metrics: Optional[Dict[str, bool]] = None,
        staff_metrics: Optional[Dict[str, bool]] = None,
        financial_metrics: Optional[Dict[str, bool]] = None,
        setup_complete: bool = True,
        auto_update_enabled: bool = False
    ) -> LibraryConfig:
        """
        Create or update the library configuration.
        
        Args:
            db: Database session
            library_id: FSCSKEY of the library
            library_name: Name of the library
            collection_stats_enabled: Whether collection statistics are enabled
            usage_stats_enabled: Whether usage statistics are enabled
            program_stats_enabled: Whether program statistics are enabled
            staff_stats_enabled: Whether staff statistics are enabled
            financial_stats_enabled: Whether financial statistics are enabled
            collection_metrics: Dictionary of collection metrics to track
            usage_metrics: Dictionary of usage metrics to track
            program_metrics: Dictionary of program metrics to track
            staff_metrics: Dictionary of staff metrics to track
            financial_metrics: Dictionary of financial metrics to track
            setup_complete: Whether setup is complete
            auto_update_enabled: Whether automatic updates are enabled
            
        Returns:
            LibraryConfig: Created or updated configuration
        """
        config = LibraryConfigService.get_library_config(db)
        
        if config is None:
            # Create new config
            config = LibraryConfig(
                library_id=library_id,
                library_name=library_name,
                collection_stats_enabled=collection_stats_enabled,
                usage_stats_enabled=usage_stats_enabled,
                program_stats_enabled=program_stats_enabled,
                staff_stats_enabled=staff_stats_enabled,
                financial_stats_enabled=financial_stats_enabled,
                collection_metrics=collection_metrics,
                usage_metrics=usage_metrics,
                program_metrics=program_metrics,
                staff_metrics=staff_metrics,
                financial_metrics=financial_metrics,
                setup_complete=setup_complete,
                auto_update_enabled=auto_update_enabled
            )
            db.add(config)
        else:
            # Update existing config
            config.library_id = library_id
            config.library_name = library_name
            config.collection_stats_enabled = collection_stats_enabled
            config.usage_stats_enabled = usage_stats_enabled
            config.program_stats_enabled = program_stats_enabled
            config.staff_stats_enabled = staff_stats_enabled
            config.financial_stats_enabled = financial_stats_enabled
            
            if collection_metrics is not None:
                config.collection_metrics = collection_metrics
            if usage_metrics is not None:
                config.usage_metrics = usage_metrics
            if program_metrics is not None:
                config.program_metrics = program_metrics
            if staff_metrics is not None:
                config.staff_metrics = staff_metrics
            if financial_metrics is not None:
                config.financial_metrics = financial_metrics
                
            config.setup_complete = setup_complete
            config.auto_update_enabled = auto_update_enabled
        
        db.commit()
        db.refresh(config)
        return config
    
    @staticmethod
    def search_libraries(db: Session, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for libraries by name or ID.
        
        Args:
            db: Database session
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List[Dict]: List of libraries matching the search
        """
        # Get the most recent dataset
        latest_dataset = db.query(Library).order_by(Library.dataset_id.desc()).first()
        
        if not latest_dataset:
            return []
        
        # Search for libraries in that dataset
        libraries = db.query(Library).filter(
            Library.dataset_id == latest_dataset.dataset_id
        ).filter(
            Library.name.ilike(f"%{query}%") | Library.library_id.ilike(f"%{query}%")
        ).limit(limit).all()
        
        return [
            {
                "id": lib.library_id,
                "name": lib.name,
                "city": lib.city,
                "state": lib.state
            }
            for lib in libraries
        ]
    
    @staticmethod
    def get_metric_categories() -> Dict[str, Dict[str, str]]:
        """
        Get available metric categories and their fields.
        
        Returns:
            Dict: Dictionary of metric categories and fields
        """
        return {
            "collection": {
                "print_collection": "Print Collection",
                "electronic_collection": "Electronic Collection",
                "audio_collection": "Audio Collection",
                "video_collection": "Video Collection"
            },
            "usage": {
                "total_circulation": "Total Circulation",
                "electronic_circulation": "Electronic Circulation",
                "physical_circulation": "Physical Circulation",
                "visits": "Visits",
                "reference_transactions": "Reference Transactions",
                "registered_users": "Registered Users",
                "public_internet_computers": "Public Internet Computers",
                "public_wifi_sessions": "Public WiFi Sessions",
                "website_visits": "Website Visits"
            },
            "program": {
                "total_programs": "Total Programs",
                "total_program_attendance": "Total Program Attendance",
                "children_programs": "Children's Programs",
                "children_program_attendance": "Children's Program Attendance",
                "ya_programs": "Young Adult Programs",
                "ya_program_attendance": "Young Adult Program Attendance",
                "adult_programs": "Adult Programs",
                "adult_program_attendance": "Adult Program Attendance"
            },
            "staff": {
                "total_staff": "Total Staff (FTE)",
                "librarian_staff": "Librarian Staff (FTE)",
                "mls_librarian_staff": "MLS Librarian Staff (FTE)",
                "other_staff": "Other Staff (FTE)"
            },
            "financial": {
                "total_operating_revenue": "Total Operating Revenue",
                "local_operating_revenue": "Local Operating Revenue",
                "state_operating_revenue": "State Operating Revenue",
                "federal_operating_revenue": "Federal Operating Revenue",
                "other_operating_revenue": "Other Operating Revenue",
                "total_operating_expenditures": "Total Operating Expenditures",
                "staff_expenditures": "Staff Expenditures",
                "collection_expenditures": "Collection Expenditures",
                "print_collection_expenditures": "Print Collection Expenditures",
                "electronic_collection_expenditures": "Electronic Collection Expenditures",
                "other_collection_expenditures": "Other Collection Expenditures",
                "other_operating_expenditures": "Other Operating Expenditures",
                "capital_revenue": "Capital Revenue",
                "capital_expenditures": "Capital Expenditures"
            }
        } 