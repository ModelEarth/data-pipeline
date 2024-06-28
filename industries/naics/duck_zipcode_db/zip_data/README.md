# Process Industries

We use naics-annual.ipynb to generate country, states and county files.

[Our Community Datasets](http://model.earth/community-data/) for industries are generated for:
- [US Country](https://github.com/ModelEarth/community-data/tree/master/industries/naics/US/country)
- [States](https://github.com/ModelEarth/community-data/tree/master/industries/naics/US/states)
- [Counties](https://github.com/ModelEarth/community-data/tree/master/industries/naics/US/counties)
- Zip - Coming soon

Zip code files are pulled from the API and saved as DuckDB (by David C)

TO DO: Output to a new zip folder at [Community-data repo](https://github.com/ModelEarth/community-data/tree/master/industries/naics/US/) 

See the format of our prior zip folder

<!-- Added variable to send older zip data. -->

<!-- not used: parameter called "loclevel" to toggle to the zip code output in the naics-annual.ipynb file. -->

### NAICS Zip Code data

Starting with 2019, [ZIP Codes Business Patterns (ZBP)](https://www.census.gov/data/developers/data-sets/cbp-zbp/zbp-api.html) are available in the  
County Business Patterns (CBP) API that use for state and county naics processing.

Old page to revise: [Processing zips codes prior to 2019](https://model.earth/community-data/process/naics/)

#### Note from David

The sqlite and zip utility folders are deprecated. We can delete them and the associated files.

Key Changes:

Replaced SQLite with DuckDB for its high-performance read capabilities.  
Updated database connection logic to use DuckDB for all data operations.  
Implemented a function that queries the database by year, industry level, and the first digit of the zipcode, which allows for more targeted data retrieval.  
Implemented a function that exports the database to csv files for better portability.  
Implemented a function that can rebuild the database from the csv files.  
Optimized export_to_csv and import_csv_files functions to handle data segmentation by year and industry level.  This makes sure that each CSV file does not greatly exceed 25MB.  


## DuckDB zip database

Located in duck\_zipcode\_db > zip\_data > duck\_db\_manager > database

**Note:** Only run the the 'populate_database' notebook if for whatever reason, you don't have the required CSV files. Otherwise, instantiating a 'DuckDBManager' object will automatically build a duckdb database from the CSV files. 

If you're looking to update the database, instantiate a 'ZipPopulator' object and then run 'get_zip_for_year(year)' in the populate_database notebook.


### Querying the database through Python (In progress)
This is a work in progress. The idea here is to make Python functions to easily query the database that would be in the 'zip_data' folder. This way, you can query data in a notebook environment, and get them in a csv file format.

# Database Structure

This database is designed to store economic data related to different zipcodes and industries. The database schema consists of four tables: `DimYear`, `DimNaics`, `DimZipCode`, and `DataEntry`. Below is an explanation of each table and its purpose.

Please note, that in the actual database, the key constraints are not enforced since they significantly slow down data ingestion. If in the future the constraints are needed, the data can be transferred to a database that does use the constraints.

## Table: DimYear

The `DimYear` table stores information about different years. It serves as a dimension table for years.

- **Year**: INTEGER, Primary Key - This is the year value.
- **YearDescription**: TEXT - This provides the NAICS code version for the specified year. For example, 'NAICS2017' is used for 2017 to at least 2023


## Table: DimNaics

The `DimNaics` table stores information about NAICS codes. It serves as a dimension table for industries.

- **NaicsCode**: TEXT - This is the NAICS code.
- **industry_detail**: TEXT - This provides a description of the industry.


## Table: DimZipCode

The `DimZipCode` table stores information about geographic locations, identified by ZIP codes. It serves as a dimension table for geographic locations.

- **GeoID**: TEXT, Primary Key - This is the geographic identifier, typically a ZIP code.
- **City**: TEXT - The city corresponding to the ZIP code.
- **State**: TEXT - The state corresponding to the ZIP code.


## Table: DataEntry

The `DataEntry` table stores economic data entries, linking geographic locations, industries, and years. It includes data about establishments, employees, and payrolls.

- **EntryID**: INTEGER, Primary Key, AUTOINCREMENT - This is a unique identifier for each data entry.
- **GeoID**: TEXT - This is a foreign key referencing the `GeoID` in the `DimZipCode` table.
- **NaicsCode**: TEXT - This is a foreign key referencing the `NaicsCode` in the `DimNaics` table.
- **Year**: INTEGER - This is a foreign key referencing the `Year` in the `DimYear` table.
- **Establishments**: INTEGER - Number of establishments.
- **Employees**: INTEGER - Number of employees.
- **Payroll**: INTEGER - Total payroll.
- **IndustryLevel**: INTEGER - Indicates the level of detail in the industry classification.


## Relationships

- The `DataEntry` table references the `DimZipCode` table through the `GeoID` foreign key.
- The `DataEntry` table references the `DimNaics` table through the `NaicsCode` foreign key.
- The `DataEntry` table references the `DimYear` table through the `Year` foreign key.

