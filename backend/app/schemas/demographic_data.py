from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator


# Base model with common attributes
class DemographicBase(BaseModel):
    """Base schema for demographic data with common attributes."""
    geographic_id: Optional[str] = None
    geographic_type: Optional[str] = None
    state: Optional[str] = None
    county: Optional[str] = None
    city: Optional[str] = None
    zip_code: Optional[str] = None


# Population schemas
class PopulationBase(DemographicBase):
    """Base schema for population data."""
    total_population: Optional[int] = None
    population_under_18: Optional[int] = None
    population_18_to_64: Optional[int] = None
    population_65_plus: Optional[int] = None
    population_male: Optional[int] = None
    population_female: Optional[int] = None
    population_white: Optional[int] = None
    population_black: Optional[int] = None
    population_hispanic: Optional[int] = None
    population_asian: Optional[int] = None
    
    # Calculate additional statistics
    @property
    def percent_under_18(self) -> Optional[float]:
        if self.total_population and self.population_under_18:
            return round((self.population_under_18 / self.total_population) * 100, 1)
        return None

    @property
    def percent_65_plus(self) -> Optional[float]:
        if self.total_population and self.population_65_plus:
            return round((self.population_65_plus / self.total_population) * 100, 1)
        return None
    
    @property
    def percent_white(self) -> Optional[float]:
        if self.total_population and self.population_white:
            return round((self.population_white / self.total_population) * 100, 1)
        return None
    
    @property
    def percent_black(self) -> Optional[float]:
        if self.total_population and self.population_black:
            return round((self.population_black / self.total_population) * 100, 1)
        return None
    
    @property
    def percent_hispanic(self) -> Optional[float]:
        if self.total_population and self.population_hispanic:
            return round((self.population_hispanic / self.total_population) * 100, 1)
        return None


class PopulationCreate(PopulationBase):
    """Schema for creating population data."""
    dataset_id: int


class PopulationUpdate(PopulationBase):
    """Schema for updating population data."""
    pass


class PopulationInDB(PopulationBase):
    """Schema for population data stored in the database."""
    id: int
    dataset_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# Economic schemas
class EconomicBase(DemographicBase):
    """Base schema for economic data."""
    median_household_income: Optional[int] = None
    per_capita_income: Optional[int] = None
    unemployment_rate: Optional[float] = None
    poverty_rate: Optional[float] = None


class EconomicCreate(EconomicBase):
    """Schema for creating economic data."""
    dataset_id: int


class EconomicUpdate(EconomicBase):
    """Schema for updating economic data."""
    pass


class EconomicInDB(EconomicBase):
    """Schema for economic data stored in the database."""
    id: int
    dataset_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# Education schemas
class EducationBase(DemographicBase):
    """Base schema for education data."""
    high_school_or_higher_percent: Optional[float] = None
    bachelors_or_higher_percent: Optional[float] = None
    population_enrolled_in_school: Optional[int] = None


class EducationCreate(EducationBase):
    """Schema for creating education data."""
    dataset_id: int


class EducationUpdate(EducationBase):
    """Schema for updating education data."""
    pass


class EducationInDB(EducationBase):
    """Schema for education data stored in the database."""
    id: int
    dataset_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# Housing schemas
class HousingBase(DemographicBase):
    """Base schema for housing data."""
    total_housing_units: Optional[int] = None
    housing_owner_occupied: Optional[int] = None
    housing_median_value: Optional[int] = None
    housing_median_gross_rent: Optional[int] = None
    
    # Calculate additional statistics
    @property
    def percent_owner_occupied(self) -> Optional[float]:
        if self.total_housing_units and self.housing_owner_occupied:
            return round((self.housing_owner_occupied / self.total_housing_units) * 100, 1)
        return None


class HousingCreate(HousingBase):
    """Schema for creating housing data."""
    dataset_id: int


class HousingUpdate(HousingBase):
    """Schema for updating housing data."""
    pass


class HousingInDB(HousingBase):
    """Schema for housing data stored in the database."""
    id: int
    dataset_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# Dataset schemas
class DemographicDatasetBase(BaseModel):
    """Base schema for demographic datasets."""
    source: str
    year: int
    date_collected: Optional[date] = None
    status: str = "pending"
    notes: Optional[str] = None


class DemographicDatasetCreate(DemographicDatasetBase):
    """Schema for creating demographic datasets."""
    pass


class DemographicDatasetUpdate(BaseModel):
    """Schema for updating demographic datasets."""
    source: Optional[str] = None
    year: Optional[int] = None
    date_collected: Optional[date] = None
    status: Optional[str] = None
    record_count: Optional[int] = None
    notes: Optional[str] = None


class DemographicDatasetInDB(DemographicDatasetBase):
    """Schema for demographic datasets stored in the database."""
    id: int
    record_count: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# Combined demographic data schema for API responses
class DemographicData(BaseModel):
    """Combined schema for demographic data used in API responses."""
    id: Optional[int] = None
    source: str
    year: int
    geographic_id: str
    geographic_name: str
    state: str
    county: Optional[str] = None
    zip_code: Optional[str] = None
    
    # Population data
    total_population: int
    median_age: Optional[float] = None
    percent_under_18: float
    percent_65_plus: float
    percent_white: float
    percent_black: float
    percent_hispanic: float
    
    # Economic data
    median_household_income: int
    poverty_rate: float
    
    # Education data
    high_school_or_higher_percent: float
    bachelors_or_higher_percent: float
    
    # Housing data
    total_housing_units: int
    percent_owner_occupied: float
    housing_median_value: int


# Schema for simplified demographic responses
class SimpleDemographicData(BaseModel):
    """Simplified schema for demographic data overview."""
    geography: dict
    population: dict
    economics: dict
    education: dict
    housing: dict
    data_source: dict 