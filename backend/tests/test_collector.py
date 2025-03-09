import os
import tempfile
from pathlib import Path
from unittest import mock

import pytest
from sqlalchemy.orm import Session

from app.services.collector import PLSDataCollector
from app.models.pls_data import PLSDataset, Library, LibraryOutlet


def test_collector_initialization(db: Session):
    """Test that the collector can be initialized with a database session."""
    collector = PLSDataCollector(db)
    assert collector.db == db
    assert isinstance(collector.data_dir, Path)
    assert collector.data_dir.exists()


@mock.patch('app.services.collector.requests.get')
def test_discover_available_years(mock_get, db: Session):
    """Test the discover_available_years method."""
    # Setup mock response
    mock_response = mock.Mock()
    mock_response.status_code = 200
    mock_response.content = """
    <html>
        <body>
            <a href="#">Public Libraries Survey FY 2020</a>
            <a href="#">Some other link</a>
            <a href="#">FY 2021 Public Libraries Survey</a>
            <a href="#">Public Libraries Survey (2022)</a>
        </body>
    </html>
    """
    mock_get.return_value = mock_response
    
    collector = PLSDataCollector(db)
    years = collector.discover_available_years()
    
    # Test that the correct years were discovered
    assert sorted(years) == [2020, 2021, 2022]
    
    # Test that the request was made with the correct URL
    mock_get.assert_called_once_with(collector.base_url)


@mock.patch('app.services.collector.PLSDataCollector.download_data_for_year')
@mock.patch('app.services.collector.PLSDataCollector.process_data_for_year')
@mock.patch('app.services.collector.PLSDataCollector.load_data_into_db')
def test_collect_data_for_year(mock_load, mock_process, mock_download, db: Session):
    """Test the collect_data_for_year method."""
    # Setup mocks
    mock_path = Path('/tmp/test.zip')
    mock_download.return_value = mock_path
    mock_data = {'libraries': None, 'outlets': None}
    mock_process.return_value = mock_data
    
    collector = PLSDataCollector(db)
    success = collector.collect_data_for_year(2022)
    
    # Test that the method returns success
    assert success is True
    
    # Test that the correct methods were called
    mock_download.assert_called_once_with(2022)
    mock_process.assert_called_once_with(2022, mock_path)
    mock_load.assert_called_once_with(2022, mock_data)


@mock.patch('app.services.collector.PLSDataCollector.collect_data_for_year')
def test_collect_data_for_years(mock_collect, db: Session):
    """Test the collect_data_for_years method."""
    # Setup mock
    mock_collect.side_effect = [True, False, True]  # Success for years 1 and 3, failure for year 2
    
    collector = PLSDataCollector(db)
    results = collector.collect_data_for_years([2020, 2021, 2022])
    
    # Test the results
    assert results == {2020: True, 2021: False, 2022: True}
    
    # Test that collect_data_for_year was called for each year
    assert mock_collect.call_count == 3
    mock_collect.assert_any_call(2020)
    mock_collect.assert_any_call(2021)
    mock_collect.assert_any_call(2022)


@mock.patch('app.services.collector.PLSDataCollector.discover_available_years')
@mock.patch('app.services.collector.PLSDataCollector.collect_data_for_years')
def test_collect_all_available_data(mock_collect_years, mock_discover, db: Session):
    """Test the collect_all_available_data method."""
    # Setup mocks
    mock_discover.return_value = [2020, 2021, 2022]
    mock_collect_years.return_value = {2020: True, 2021: True, 2022: True}
    
    collector = PLSDataCollector(db)
    results = collector.collect_all_available_data()
    
    # Test the results
    assert results == {2020: True, 2021: True, 2022: True}
    
    # Test that the correct methods were called
    mock_discover.assert_called_once()
    mock_collect_years.assert_called_once_with([2020, 2021, 2022])


@mock.patch('app.services.collector.PLSDataCollector.discover_available_years')
@mock.patch('app.services.collector.PLSDataCollector.collect_data_for_year')
def test_update_with_latest_data(mock_collect, mock_discover, db: Session):
    """Test the update_with_latest_data method."""
    # Setup mocks
    mock_discover.return_value = [2020, 2021, 2022]
    mock_collect.return_value = True
    
    # Create a dataset for an earlier year
    dataset = PLSDataset(year=2021, status="complete", record_count=100)
    db.add(dataset)
    db.commit()
    
    collector = PLSDataCollector(db)
    latest_year = collector.update_with_latest_data()
    
    # Test that the latest year was returned
    assert latest_year == 2022
    
    # Test that the correct methods were called
    mock_discover.assert_called_once()
    mock_collect.assert_called_once_with(2022)


@mock.patch('app.services.collector.PLSDataCollector.discover_available_years')
@mock.patch('app.services.collector.PLSDataCollector.collect_data_for_year')
def test_update_with_latest_data_already_exists(mock_collect, mock_discover, db: Session):
    """Test the update_with_latest_data method when the latest data already exists."""
    # Setup mocks
    mock_discover.return_value = [2020, 2021, 2022]
    
    # Create a dataset for the latest year
    dataset = PLSDataset(year=2022, status="complete", record_count=100)
    db.add(dataset)
    db.commit()
    
    collector = PLSDataCollector(db)
    latest_year = collector.update_with_latest_data()
    
    # Test that no year was returned (no update needed)
    assert latest_year is None
    
    # Test that the discover method was called but not the collect method
    mock_discover.assert_called_once()
    mock_collect.assert_not_called() 