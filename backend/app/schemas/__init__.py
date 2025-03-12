# Import all schemas here for easy access
from app.schemas.pls_data import (
    PLSDataset, 
    Library, 
    LibraryOutlet,
    PLSDatasetCreate,
    LibraryCreate,
    LibraryOutletCreate,
    PLSDatasetWithRelations,
    PLSDatasetUpdate,
    LibraryUpdate,
    LibraryOutletUpdate,
    DatasetCreate,
    DatasetUpdate,
    Dataset,
    PLSData,
    PLSDataCreate,
    PLSDataUpdate
)

from app.schemas.library_config import (
    LibraryConfig,
    LibraryConfigCreate,
    LibraryConfigUpdate
)

from app.schemas.demographic_data import (
    DemographicData,
    SimpleDemographicData,
    DemographicDatasetCreate,
    DemographicDatasetUpdate,
    DemographicDatasetInDB,
    PopulationCreate,
    PopulationUpdate,
    PopulationInDB,
    EconomicCreate,
    EconomicUpdate,
    EconomicInDB,
    EducationCreate,
    EducationUpdate,
    EducationInDB,
    HousingCreate,
    HousingUpdate,
    HousingInDB
) 