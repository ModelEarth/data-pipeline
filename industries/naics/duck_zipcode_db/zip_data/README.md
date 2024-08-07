# Process NAICS Industries

### For use in local US EPA impact comparisons

We use naics-annual.ipynb to generate country, states and county files.

[Our Community Datasets](http://model.earth/community-data/) for industries are generated for:
- [US Country](https://github.com/ModelEarth/community-data/tree/master/industries/naics/US/country)
- [States](https://github.com/ModelEarth/community-data/tree/master/industries/naics/US/states)
- [Counties](https://github.com/ModelEarth/community-data/tree/master/industries/naics/US/counties)
- [Zip](https://github.com/ModelEarth/community-data/tree/master/industries/naics/US/) - Coming soon



### Process Industry NAICS by Zip Code

**Each zip code .csv will have these 6 columns:**

- Zip - Only in counties files.
- Naics - ActivityProducedBy (6-digit naics)  
- Establishments - Other (Number of Extablishments)  
- Employees - Employment FlowAmount (Number of Employees)  
- Payroll - US Dollars (Annual Wages)

Folders are nested 3/0/3/1/8 to avoid GitHub's files-per-folder limit.

The results will be used in our [Industry Comparison location filters](https://model.earth/localsite/info/#geoview=state&state=NY), similar to countries, states and counties.

The old zip code files reside here:  
[community-data/us/zipcodes/naics](https://github.com/ModelEarth/community-data/tree/master/us/zipcodes/naics/) - [30318](https://github.com/ModelEarth/community-data/blob/master/us/zipcodes/naics/3/0/3/1/8/zipcode30318-census-naics6-2018.csv)

The new zip code files will reside at:  
[community-data/industries/naics/US/zip](https://github.com/ModelEarth/community-data/tree/master/industries/naics/US/)


For each year, there will be 5 zip code files for each state:  

US/zip/NY/US-NY-census-naics2-zip-2023.csv  
US/zip/NY/US-NY-census-naics3-zip-2023.csv  
US/zip/NY/US-NY-census-naics4-zip-2023.csv  
US/zip/NY/US-NY-census-naics5-zip-2023.csv  
US/zip/NY/US-NY-census-naics6-zip-2023.csv  

Some payroll fields provide from the census will be null to protect privacy.
Here's our work on [Estimating using Machine Learning](https://model.earth/machine-learning/)


Zip code files are pulled from the Census API and saved as DuckDB here in the [duck\_zipcode\_db](https://github.com/ModelEarth/data-pipeline/tree/main/industries/naics/duck_zipcode_db) subfolder (by David C in June 2024)

DuckDB is faster at processing than Pandas. The DuckDB database was too big to deploy to GitHub.

TO DO: Create DuckDB files by year so they are small enough to share with GitHub.

TO DO: Process new data once a year using a GitHub Action.

David included additional fields like city in the DuckDB, which could be useful later for filling in gaps with ML.

In July, Badri ran this in VS Code terminal. Launch in "naics" folder using `code .`

	python3 -m venv env
	source env/bin/activate
	python -m pip install ipykernel -U --force-reinstall
	pip install duckdb
	pip install pandas
	pip install tqdm

Hit "Change Kernel"

**Go to:** naics/duck\_zipcode\_db/zip\_data/duck\_db\_manager/duckdb\_database.ipynb

Run the 1st and 4th cells in duckdb\_database.ipynb

TO DO: Make the notebook intuitive by eliminating the need to skip a step.  
Move retained files to naics/duckdb/prep. Use dashes instead of underscores in files names.

TO DO: Output nested folders within a new "zip" folder in a fork of [community-data/industries/naics/US/zip](https://github.com/ModelEarth/community-data/tree/master/industries/naics/US/) 

TO DO: This process needs to be run annually via a Github Action. We could avoid sending to DuckDB when just updating one year at a time.

<!-- Added variable to send older zip data. -->

<!-- not used: parameter called "loclevel" to toggle to the zip code output in the naics-annual.ipynb file. -->

### NAICS Zip Code data

Starting with 2019, [ZIP Codes Business Patterns (ZBP)](https://www.census.gov/data/developers/data-sets/cbp-zbp/zbp-api.html) are available in the  
County Business Patterns (CBP) API that use for state and county naics processing.

Old page to revise: [Processing zips codes prior to 2019](https://model.earth/community-data/process/naics/)

#### Note from David

The sqlite and zip utility folders are deprecated. We can delete them and the associated files.

TO DO: Delete the folders as David has advised. Thanks!

Key Changes (this is a note from David):

Replaced SQLite with DuckDB for its high-performance read capabilities.  
Updated database connection logic to use DuckDB for all data operations.  
Implemented a function that queries the database by year, industry level, and the first digit of the zipcode, which allows for more targeted data retrieval.  
Implemented a function that exports the database to csv files for better portability.  
Implemented a function that can rebuild the database from the csv files.  
Optimized export\_to\_csv and import\_csv\_files functions to handle data segmentation by year and industry level.  This makes sure that each CSV file does not greatly exceed 25MB. (Loren adds: Let's avoid deploying the year-industry files. We could instead rebuild DuckDB from the zipcode files in 3/0/3/1/8 folders.)  

Also from David:

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

