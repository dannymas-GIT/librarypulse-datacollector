from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.pls_data import PLSDataset, Library, LibraryOutlet


def test_read_root(client: TestClient):
    """Test that the root endpoint returns the expected data."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["name"] == "IMLS Library Pulse"
    assert "version" in response.json()
    assert "docs_url" in response.json()


def test_health_check(client: TestClient):
    """Test that the health check endpoint returns OK."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_get_datasets_empty(client: TestClient, db: Session):
    """Test that the datasets endpoint returns an empty list when no datasets exist."""
    response = client.get("/api/v1/datasets/")
    assert response.status_code == 200
    assert response.json() == []


def test_get_available_years_empty(client: TestClient, db: Session):
    """Test that the available years endpoint returns an empty list when no datasets exist."""
    response = client.get("/api/v1/datasets/years/available")
    assert response.status_code == 200
    assert response.json() == []


def test_create_and_get_dataset(client: TestClient, db: Session):
    """Test creating a dataset and then retrieving it."""
    # Create a test dataset
    dataset = PLSDataset(year=2022, status="complete", record_count=100)
    db.add(dataset)
    db.commit()
    
    # Test that we can retrieve the dataset
    response = client.get("/api/v1/datasets/")
    assert response.status_code == 200
    datasets = response.json()
    assert len(datasets) == 1
    assert datasets[0]["year"] == 2022
    assert datasets[0]["status"] == "complete"
    assert datasets[0]["record_count"] == 100
    
    # Test that we can retrieve the dataset by year
    response = client.get("/api/v1/datasets/2022")
    assert response.status_code == 200
    dataset_data = response.json()
    assert dataset_data["year"] == 2022
    assert dataset_data["status"] == "complete"
    assert dataset_data["record_count"] == 100
    
    # Test the available years endpoint
    response = client.get("/api/v1/datasets/years/available")
    assert response.status_code == 200
    years = response.json()
    assert years == [2022]


def test_get_nonexistent_dataset(client: TestClient, db: Session):
    """Test that requesting a nonexistent dataset returns a 404."""
    response = client.get("/api/v1/datasets/9999")
    assert response.status_code == 404


def test_libraries_endpoints(client: TestClient, db: Session):
    """Test the basic functionality of the libraries endpoints."""
    # Create a test dataset
    dataset = PLSDataset(year=2022, status="complete", record_count=100)
    db.add(dataset)
    db.commit()
    
    # Create a test library
    library = Library(
        dataset_id=dataset.id,
        library_id="TEST01",
        name="Test Library",
        state="CA",
        county="Test County",
        service_area_population=10000,
        total_circulation=50000,
        visits=20000,
        total_staff=10.5
    )
    db.add(library)
    db.commit()
    
    # Test that we can retrieve libraries
    response = client.get("/api/v1/libraries/")
    assert response.status_code == 200
    libraries = response.json()
    assert len(libraries) == 1
    assert libraries[0]["library_id"] == "TEST01"
    assert libraries[0]["name"] == "Test Library"
    assert libraries[0]["state"] == "CA"
    
    # Test filtering by state
    response = client.get("/api/v1/libraries/?state=CA")
    assert response.status_code == 200
    libraries = response.json()
    assert len(libraries) == 1
    
    response = client.get("/api/v1/libraries/?state=NY")
    assert response.status_code == 200
    libraries = response.json()
    assert len(libraries) == 0
    
    # Test getting a specific library
    response = client.get(f"/api/v1/libraries/TEST01")
    assert response.status_code == 200
    library_data = response.json()
    assert library_data["library_id"] == "TEST01"
    assert library_data["name"] == "Test Library"
    
    # Test getting states list
    response = client.get("/api/v1/libraries/states/list")
    assert response.status_code == 200
    states = response.json()
    assert states == ["CA"]
    
    # Test getting counties list
    response = client.get("/api/v1/libraries/counties/list?state=CA")
    assert response.status_code == 200
    counties = response.json()
    assert counties == ["Test County"]


def test_stats_endpoints(client: TestClient, db: Session):
    """Test the basic functionality of the statistics endpoints."""
    # Create a test dataset
    dataset = PLSDataset(year=2022, status="complete", record_count=100)
    db.add(dataset)
    db.commit()
    
    # Create a test library
    library = Library(
        dataset_id=dataset.id,
        library_id="TEST01",
        name="Test Library",
        state="CA",
        county="Test County",
        service_area_population=10000,
        total_circulation=50000,
        visits=20000,
        total_staff=10.5,
        total_operating_revenue=1000000,
        total_operating_expenditures=900000
    )
    db.add(library)
    db.commit()
    
    # Test summary statistics
    response = client.get("/api/v1/stats/summary")
    assert response.status_code == 200
    stats = response.json()
    assert stats["year"] == 2022
    assert stats["library_count"] == 1
    assert stats["total_visits"] == 20000
    assert stats["total_circulation"] == 50000
    
    # Test with state filter
    response = client.get("/api/v1/stats/summary?state=CA")
    assert response.status_code == 200
    stats = response.json()
    assert stats["state"] == "CA"
    assert stats["total_visits"] == 20000
    
    # Test with invalid state
    response = client.get("/api/v1/stats/summary?state=XX")
    assert response.status_code == 404
    
    # Test trends
    response = client.get("/api/v1/stats/trends?metrics=visits&metrics=total_circulation")
    assert response.status_code == 200
    trends = response.json()
    assert "years" in trends
    assert "visits" in trends
    assert "total_circulation" in trends
    assert trends["years"] == [2022]
    assert trends["visits"] == [20000]
    assert trends["total_circulation"] == [50000]
    
    # Test comparison
    response = client.get("/api/v1/stats/comparison?library_ids=TEST01")
    assert response.status_code == 200
    comparison = response.json()
    assert comparison["year"] == 2022
    assert len(comparison["libraries"]) == 1
    assert comparison["libraries"][0]["library_id"] == "TEST01"
    assert "visits" in comparison["libraries"][0]["metrics"]
    assert comparison["libraries"][0]["metrics"]["visits"]["value"] == 20000 