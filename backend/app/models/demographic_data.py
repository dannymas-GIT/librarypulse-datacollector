from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Date, Text, Enum, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base import Base, IDMixin, TimestampMixin


class DemographicDataset(Base, IDMixin, TimestampMixin):
    """Model representing a demographic dataset from the Census or other sources."""
    
    __tablename__ = "demographic_datasets"
    
    source = Column(String(100), nullable=False, index=True)  # "Census ACS", "Census Decennial", etc.
    year = Column(Integer, nullable=False, index=True)
    date_collected = Column(Date, nullable=True)
    status = Column(String(20), nullable=False, default="pending")  # pending, processing, complete, error
    record_count = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Creates a unique constraint on source and year
    __table_args__ = (UniqueConstraint('source', 'year', name='uix_demographic_source_year'),)
    
    # Relationships
    population_data = relationship("PopulationData", back_populates="dataset", cascade="all, delete-orphan")
    economic_data = relationship("EconomicData", back_populates="dataset", cascade="all, delete-orphan")
    education_data = relationship("EducationData", back_populates="dataset", cascade="all, delete-orphan")
    language_data = relationship("LanguageData", back_populates="dataset", cascade="all, delete-orphan")
    housing_data = relationship("HousingData", back_populates="dataset", cascade="all, delete-orphan")


class PopulationData(Base, IDMixin, TimestampMixin):
    """Model representing population statistics for a specific geographic area."""
    
    __tablename__ = "population_data"
    
    dataset_id = Column(Integer, ForeignKey("demographic_datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    geographic_id = Column(String(20), nullable=False, index=True)  # FIPS code or other geographic identifier
    geographic_type = Column(String(50), nullable=False, index=True)  # "County", "ZIP", "Census Tract", etc.
    
    # Geographic identifiers
    state = Column(String(2), nullable=False, index=True)
    county = Column(String(100), nullable=True, index=True)
    city = Column(String(100), nullable=True, index=True)
    zip_code = Column(String(10), nullable=True, index=True)
    
    # Total population
    total_population = Column(Integer, nullable=True)
    
    # Population by age ranges
    population_under_5 = Column(Integer, nullable=True)
    population_5_to_9 = Column(Integer, nullable=True)
    population_10_to_14 = Column(Integer, nullable=True)
    population_15_to_19 = Column(Integer, nullable=True)
    population_20_to_24 = Column(Integer, nullable=True)
    population_25_to_34 = Column(Integer, nullable=True)
    population_35_to_44 = Column(Integer, nullable=True)
    population_45_to_54 = Column(Integer, nullable=True)
    population_55_to_59 = Column(Integer, nullable=True)
    population_60_to_64 = Column(Integer, nullable=True)
    population_65_to_74 = Column(Integer, nullable=True)
    population_75_to_84 = Column(Integer, nullable=True)
    population_85_plus = Column(Integer, nullable=True)
    
    # Population by sex
    population_male = Column(Integer, nullable=True)
    population_female = Column(Integer, nullable=True)
    
    # Population by race/ethnicity
    population_white = Column(Integer, nullable=True)
    population_black = Column(Integer, nullable=True)
    population_hispanic = Column(Integer, nullable=True)
    population_asian = Column(Integer, nullable=True)
    population_native = Column(Integer, nullable=True)
    population_pacific_islander = Column(Integer, nullable=True)
    population_other_race = Column(Integer, nullable=True)
    population_two_or_more_races = Column(Integer, nullable=True)
    
    # Household data
    total_households = Column(Integer, nullable=True)
    avg_household_size = Column(Float, nullable=True)
    households_with_children = Column(Integer, nullable=True)
    family_households = Column(Integer, nullable=True)
    nonfamily_households = Column(Integer, nullable=True)
    
    # Relationship
    dataset = relationship("DemographicDataset", back_populates="population_data")


class EconomicData(Base, IDMixin, TimestampMixin):
    """Model representing economic statistics for a specific geographic area."""
    
    __tablename__ = "economic_data"
    
    dataset_id = Column(Integer, ForeignKey("demographic_datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    geographic_id = Column(String(20), nullable=False, index=True)  # FIPS code or other geographic identifier
    geographic_type = Column(String(50), nullable=False, index=True)  # "County", "ZIP", "Census Tract", etc.
    
    # Geographic identifiers
    state = Column(String(2), nullable=False, index=True)
    county = Column(String(100), nullable=True, index=True)
    city = Column(String(100), nullable=True, index=True)
    zip_code = Column(String(10), nullable=True, index=True)
    
    # Income data
    median_household_income = Column(Integer, nullable=True)
    mean_household_income = Column(Integer, nullable=True)
    per_capita_income = Column(Integer, nullable=True)
    
    # Income ranges
    households_income_less_10k = Column(Integer, nullable=True)
    households_income_10k_15k = Column(Integer, nullable=True)
    households_income_15k_25k = Column(Integer, nullable=True)
    households_income_25k_35k = Column(Integer, nullable=True)
    households_income_35k_50k = Column(Integer, nullable=True)
    households_income_50k_75k = Column(Integer, nullable=True)
    households_income_75k_100k = Column(Integer, nullable=True)
    households_income_100k_150k = Column(Integer, nullable=True)
    households_income_150k_200k = Column(Integer, nullable=True)
    households_income_200k_plus = Column(Integer, nullable=True)
    
    # Employment data
    population_in_labor_force = Column(Integer, nullable=True)
    population_employed = Column(Integer, nullable=True)
    population_unemployed = Column(Integer, nullable=True)
    unemployment_rate = Column(Float, nullable=True)
    
    # Poverty data
    population_below_poverty_level = Column(Integer, nullable=True)
    poverty_rate = Column(Float, nullable=True)
    
    # Relationship
    dataset = relationship("DemographicDataset", back_populates="economic_data")


class EducationData(Base, IDMixin, TimestampMixin):
    """Model representing education statistics for a specific geographic area."""
    
    __tablename__ = "education_data"
    
    dataset_id = Column(Integer, ForeignKey("demographic_datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    geographic_id = Column(String(20), nullable=False, index=True)  # FIPS code or other geographic identifier
    geographic_type = Column(String(50), nullable=False, index=True)  # "County", "ZIP", "Census Tract", etc.
    
    # Geographic identifiers
    state = Column(String(2), nullable=False, index=True)
    county = Column(String(100), nullable=True, index=True)
    city = Column(String(100), nullable=True, index=True)
    zip_code = Column(String(10), nullable=True, index=True)
    
    # Population 25 years and over
    population_25_plus = Column(Integer, nullable=True)
    
    # Educational attainment for population 25+
    population_less_than_9th_grade = Column(Integer, nullable=True)
    population_9th_to_12th_no_diploma = Column(Integer, nullable=True)
    population_high_school_graduate = Column(Integer, nullable=True)
    population_some_college_no_degree = Column(Integer, nullable=True)
    population_associates_degree = Column(Integer, nullable=True)
    population_bachelors_degree = Column(Integer, nullable=True)
    population_graduate_degree = Column(Integer, nullable=True)
    
    # School enrollment
    population_enrolled_in_school = Column(Integer, nullable=True)
    population_enrolled_preschool = Column(Integer, nullable=True)
    population_enrolled_kindergarten = Column(Integer, nullable=True)
    population_enrolled_elementary = Column(Integer, nullable=True)
    population_enrolled_high_school = Column(Integer, nullable=True)
    population_enrolled_college = Column(Integer, nullable=True)
    
    # Relationship
    dataset = relationship("DemographicDataset", back_populates="education_data")


class LanguageData(Base, IDMixin, TimestampMixin):
    """Model representing language statistics for a specific geographic area."""
    
    __tablename__ = "language_data"
    
    dataset_id = Column(Integer, ForeignKey("demographic_datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    geographic_id = Column(String(20), nullable=False, index=True)  # FIPS code or other geographic identifier
    geographic_type = Column(String(50), nullable=False, index=True)  # "County", "ZIP", "Census Tract", etc.
    
    # Geographic identifiers
    state = Column(String(2), nullable=False, index=True)
    county = Column(String(100), nullable=True, index=True)
    city = Column(String(100), nullable=True, index=True)
    zip_code = Column(String(10), nullable=True, index=True)
    
    # Language data for population 5 years and over
    population_5_plus = Column(Integer, nullable=True)
    
    # Language spoken at home
    population_english_only = Column(Integer, nullable=True)
    population_spanish = Column(Integer, nullable=True)
    population_spanish_limited_english = Column(Integer, nullable=True)
    population_indo_european = Column(Integer, nullable=True)
    population_indo_european_limited_english = Column(Integer, nullable=True)
    population_asian_pacific = Column(Integer, nullable=True)
    population_asian_pacific_limited_english = Column(Integer, nullable=True)
    population_other_languages = Column(Integer, nullable=True)
    population_other_languages_limited_english = Column(Integer, nullable=True)
    
    # Relationship
    dataset = relationship("DemographicDataset", back_populates="language_data")


class HousingData(Base, IDMixin, TimestampMixin):
    """Model representing housing statistics for a specific geographic area."""
    
    __tablename__ = "housing_data"
    
    dataset_id = Column(Integer, ForeignKey("demographic_datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    geographic_id = Column(String(20), nullable=False, index=True)  # FIPS code or other geographic identifier
    geographic_type = Column(String(50), nullable=False, index=True)  # "County", "ZIP", "Census Tract", etc.
    
    # Geographic identifiers
    state = Column(String(2), nullable=False, index=True)
    county = Column(String(100), nullable=True, index=True)
    city = Column(String(100), nullable=True, index=True)
    zip_code = Column(String(10), nullable=True, index=True)
    
    # Housing units
    total_housing_units = Column(Integer, nullable=True)
    housing_units_occupied = Column(Integer, nullable=True)
    housing_units_vacant = Column(Integer, nullable=True)
    
    # Occupancy
    housing_owner_occupied = Column(Integer, nullable=True)
    housing_renter_occupied = Column(Integer, nullable=True)
    
    # Housing characteristics
    housing_median_value = Column(Integer, nullable=True)
    housing_median_gross_rent = Column(Integer, nullable=True)
    
    # Year structure built
    housing_built_2010_or_later = Column(Integer, nullable=True)
    housing_built_2000_to_2009 = Column(Integer, nullable=True)
    housing_built_1990_to_1999 = Column(Integer, nullable=True)
    housing_built_1980_to_1989 = Column(Integer, nullable=True)
    housing_built_1970_to_1979 = Column(Integer, nullable=True)
    housing_built_1960_to_1969 = Column(Integer, nullable=True)
    housing_built_1950_to_1959 = Column(Integer, nullable=True)
    housing_built_1940_to_1949 = Column(Integer, nullable=True)
    housing_built_1939_or_earlier = Column(Integer, nullable=True)
    
    # Relationship
    dataset = relationship("DemographicDataset", back_populates="housing_data") 