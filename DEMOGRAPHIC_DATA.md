# Demographic Data Implementation

This document provides detailed information about the demographic data implementation in the Library Pulse application.

## Overview

Library Pulse integrates demographic data from the American Community Survey (ACS) to provide library administrators with insights into the communities they serve. This data helps libraries make informed decisions about services, collections, and programs based on the demographic makeup of their service areas.

## Data Source

- **American Community Survey (ACS) 5-Year Estimates (2017-2021)**
- Collected by the US Census Bureau
- Provides detailed demographic information for ZIP Code Tabulation Areas (ZCTAs)
- Updated annually with new 5-year estimates

## Database Structure

The demographic data is stored in several related tables:

- **demographic_datasets**: Metadata about demographic data sources (ACS, Census, etc.)
- **population_data**: Population statistics (total, age distribution, racial demographics)
- **economic_data**: Economic indicators (income, poverty rates, employment)
- **education_data**: Education statistics (attainment levels, enrollment)
- **housing_data**: Housing information (units, ownership, property values)

## API Endpoints

The demographic data is accessible through several API endpoints:

- **/demographics/west-babylon**: Returns demographic data for West Babylon, NY (ZCTA 11704)
- **/demographics/by-zip/{zip_code}**: Returns demographic data for a specific ZIP code
- **/demographics/for-library/{library_id}**: Returns demographic data for a library's service area

## Frontend Components

The demographic data is displayed in the frontend using dedicated components:

- **DemographicDataPanel**: Main component for displaying demographic data
  - Shows population, economic, education, and housing statistics
  - Formats numbers with appropriate commas and decimal places
  - Calculates percentages for age groups and other metrics
  - Provides a clean, organized layout for demographic information

## Data Flow

The demographic data follows a complete flow from source to UI:

1. **Data Collection**: Census ACS data is retrieved via API
2. **Processing**: Data is processed and standardized for storage
3. **Database Storage**: Processed data is stored in PostgreSQL tables
4. **API Layer**: FastAPI endpoints provide access to the demographic data
5. **Frontend Fetching**: React components fetch data using React Query
6. **UI Display**: Data is displayed in organized sections with proper formatting

## Verification

The demographic data has been verified through each step of the process:

- Database queries confirm correct storage and retrieval
- API responses match expected data structure
- Frontend components correctly display the data with appropriate formatting
- End-to-end testing validates the complete data flow

## Future Plans

### Library Comparison Features

1. **Setup Wizard Implementation**
   - Library selection step with search functionality
   - Comparison libraries step with recommendations based on:
     - Geographic proximity
     - Demographic similarity
     - Service area overlap
   - Data sources selection for metric prioritization

2. **Comparison Features**
   - Extended DemographicDataPanel for multiple libraries
   - Side-by-side comparison views
   - Visual indicators for significant differences
   - Charts for direct metric comparisons
   - Maps for geographic distribution

3. **User-Friendly Analysis Tools**
   - Drag-and-drop interface for selecting comparison metrics
   - Simple filtering options
   - Preset comparison templates

### Technical Implementation Roadmap

1. **API Extensions**
   - `/demographics/compare` endpoint for multiple libraries
   - Parameter support for filtering specific metrics
   - Caching for frequently compared libraries

2. **Component Updates**
   - Make DemographicDataPanel accept library arrays
   - Create ComparisonDashboard component
   - Develop reusable chart components

3. **Data Management**
   - Store user comparison preferences
   - Create system for saving and sharing reports
   - Schedule regular data updates

## Example API Response

```json
{
  "geography": {
    "name": "West Babylon",
    "zcta": "11704",
    "state": "NY",
    "county": "Suffolk"
  },
  "population": {
    "total": 40344,
    "median_age": 43.4,
    "by_age": {
      "under_18": 6885,
      "over_65": 7890
    },
    "by_race": {
      "white": 29572,
      "black": 5180,
      "hispanic": 6469
    }
  },
  "economics": {
    "median_household_income": 96235,
    "poverty_rate": 5.2
  },
  "education": {
    "high_school_or_higher": 100.0,
    "bachelors_or_higher": 44.9
  },
  "housing": {
    "total_units": 14526,
    "owner_occupied": 11620,
    "median_home_value": 395200
  },
  "data_source": {
    "name": "American Community Survey 5-Year Estimates",
    "year": "2017-2021"
  }
}
```

## Usage Guidelines

### When to Use Demographic Data

- **Service Planning**: Align library services with community demographics
- **Collection Development**: Adjust collections based on language distribution
- **Program Design**: Create programs that meet the needs of specific age groups
- **Budget Allocation**: Allocate resources based on population characteristics
- **Grant Applications**: Support funding requests with demographic insights
- **Strategic Planning**: Make long-term plans based on community trends

### Integration with Library Metrics

Demographic data is most powerful when integrated with library usage metrics:

- Compare circulation metrics with education levels
- Analyze program attendance in relation to age distribution
- Assess digital resource usage against income and education metrics
- Evaluate service hours in context of working population percentages

## Limitations and Considerations

- ACS 5-Year Estimates represent data collected over 5 years, not a single point in time
- ZIP code boundaries may not perfectly align with library service areas
- Demographics change over time, so regular data updates are important
- Some detailed demographic breakdowns may have high margins of error
- Use demographic data as one input for decision-making, not as the sole factor

## Support and Feedback

For questions about demographic data implementation or suggestions for improvements, please contact the development team or open an issue in the project repository. 