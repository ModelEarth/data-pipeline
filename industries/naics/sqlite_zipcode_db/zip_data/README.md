# Note: 
Only run the the 'populate_database' notebook if you need to either build the sqlite database from scratch, or if you need to download new data. 

If you don't have the database you need, go to https://drive.google.com/file/d/1J1TLVkvnEQvX31MxdF2df04BNpiaExyf/view?usp=sharing and then place it in the zip_data folder.

If you are downloading new data, make sure to put the database in the folder 'zip_data'. It will make the download a lot faster. After you get the updated data, don't forget to replace the google drive link above! 

# Querying the database through Python (In progress)
This is a work in progress. The idea here is to make Python functions to easily query the database that would be in the 'zip_data' folder. This way, you can query data in a notebook environment, and get them in a csv file format.

# Database Structure

This database is designed to store economic data related to different zipcodes and industries. The database schema consists of four tables: `DimYear`, `DimNaics`, `DimZipCode`, and `DataEntry`. Below is an explanation of each table and its purpose.

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

