import duckdb
import os
import pandas as pd
from tqdm import tqdm
import os
import math

class DuckDBManager:
    def __init__(self, db_path='database/us_economic_data.duckdb', export_dir='database/exported_tables'):
        self.db_path = db_path
        self.export_dir = export_dir
        self._connect_db()
        self._close_db()

    def _connect_db(self):
        try:
            if os.path.exists(self.db_path):
                self.conn = duckdb.connect(self.db_path)
            else:
                print(f"Database {self.db_path} does not exist. Creating new database...")
                self.conn = duckdb.connect(self.db_path)
                self._create_tables()
                self.import_all_csv_files()
                self.create_indexes()
        except Exception as e:
            print(f"Error connecting to database or initializing: {e}")

    def _close_db(self):
        try:
            if self.conn:
                self.conn.close()
                self.conn = None
        except Exception as e:
            print(f"Error closing database connection: {e}")
            
    def create_indexes(self):
        self._connect_db()
        print("Creating indexes...")
        index_queries = [
            ('CREATE INDEX IF NOT EXISTS idx_GeoID ON DimZipCode(GeoID)', 'Index on GeoID in DimZipCode'),
            ('CREATE INDEX IF NOT EXISTS idx_NaicsCode ON DimNaics(NaicsCode)', 'Index on NaicsCode in DimNaics'),
            ('CREATE INDEX IF NOT EXISTS idx_Year ON DimYear(Year)', 'Index on Year in DimYear'),
            ('CREATE INDEX IF NOT EXISTS idx_EntryID ON DataEntry(EntryID)', 'Index on EntryID in DataEntry'),
            ('CREATE INDEX IF NOT EXISTS idx_GeoID_DataEntry ON DataEntry(GeoID)', 'Index on GeoID in DataEntry'),
            ('CREATE INDEX IF NOT EXISTS idx_NaicsCode_DataEntry ON DataEntry(NaicsCode)', 'Index on NaicsCode in DataEntry')
        ]

        try:
            for query, description in tqdm(index_queries, desc="Creating Indexes"):
                tqdm.write(f"Creating Index for {description}...")
                self.conn.execute(query)
                tqdm.write(f"{description} created successfully.")
        except Exception as e:
            print(f"Error creating indexes: {e}")
        finally:
            self._close_db()

    def _create_tables(self):
        try:
            if self.conn:
                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS DimZipCode (
                        GeoID VARCHAR,
                        City TEXT,
                        State TEXT
                    )
                ''')
                
                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS DimNaics (
                        NaicsCode VARCHAR,
                        industry_detail TEXT
                    )
                ''')
                
                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS DimYear (
                        Year INTEGER,
                        YearDescription TEXT
                    )
                ''')

                self.conn.execute('''
                    CREATE TABLE IF NOT EXISTS DataEntry (
                        EntryID INTEGER,
                        GeoID VARCHAR,
                        NaicsCode VARCHAR,
                        Year INTEGER,
                        Establishments INTEGER,
                        Employees INTEGER,
                        Payroll INTEGER,
                        IndustryLevel INT
                    )
                ''')
        except Exception as e:
            print(f"Error creating tables: {e}")


    def save_to_csv(self):
        try:
            self._connect_db()
            os.makedirs(self.export_dir, exist_ok=True)
            
            self.conn.execute(f"COPY (SELECT * FROM DimNaics) TO '{self.export_dir}/DimNaics.csv' WITH (FORMAT CSV, HEADER TRUE)")
            self.conn.execute(f"COPY (SELECT * FROM DimZipCode) TO '{self.export_dir}/DimZipCode.csv' WITH (FORMAT CSV, HEADER TRUE)")
            self.conn.execute(f"COPY (SELECT * FROM DimYear) TO '{self.export_dir}/DimYear.csv' WITH (FORMAT CSV, HEADER TRUE)")

            # Get the list of valid years from DimYear
            valid_years = self.conn.execute("SELECT Year FROM DimYear").fetchall()
            # Define the known industry levels
            industry_levels = [2, 4, 6]
            
            # Define maximum file size in bytes (25MB)
            max_file_size = 25 * 1024 * 1024

            # Loop through each valid year and industry level to export the corresponding DataEntry data
            for year_tuple in tqdm(valid_years, desc="Saving DataEntry CSV files"):
                year = year_tuple[0]  # Extract the year from the tuple
                for industry_level in industry_levels:
                    # Get the total number of rows for the current year and industry level
                    total_rows_query = f"""
                    SELECT COUNT(*) FROM DataEntry
                    WHERE Year = {year} AND IndustryLevel = {industry_level}
                    """
                    total_rows = self.conn.execute(total_rows_query).fetchone()[0]

                    if total_rows == 0:
                        continue

                    # Estimate the number of chunks based on the average row size
                    avg_row_size_query = f"""
                    SELECT AVG(LENGTH(CAST(EntryID AS VARCHAR)) + 
                            LENGTH(CAST(GeoID AS VARCHAR)) + 
                            LENGTH(CAST(NaicsCode AS VARCHAR)) + 
                            LENGTH(CAST(Year AS VARCHAR)) + 
                            LENGTH(CAST(Establishments AS VARCHAR)) + 
                            LENGTH(CAST(Employees AS VARCHAR)) + 
                            LENGTH(CAST(Payroll AS VARCHAR)) + 
                            LENGTH(CAST(IndustryLevel AS VARCHAR))) 
                    FROM DataEntry
                    WHERE Year = {year} AND IndustryLevel = {industry_level}
                    """
                    avg_row_size = self.conn.execute(avg_row_size_query).fetchone()[0]

                    if avg_row_size is None:
                        avg_row_size = 500

                    rows_per_chunk = math.ceil(max_file_size / avg_row_size)

                    # Export data in chunks
                    for start in range(0, total_rows, rows_per_chunk):
                        chunk_file_path = f'{self.export_dir}/DataEntry_{year}_IndustryLevel_{industry_level}_chunk_{start // rows_per_chunk}.csv'
                        
                        # Execute the query and export the data
                        query = f"""
                        COPY (
                            SELECT * 
                            FROM DataEntry
                            WHERE Year = {year} AND IndustryLevel = {industry_level}
                            LIMIT {rows_per_chunk} OFFSET {start}
                        ) TO '{chunk_file_path}' WITH (FORMAT CSV, HEADER TRUE)
                        """
                        self.conn.execute(query)
        except Exception as e:
            print(f"An error occurred during CSV export: {e}")
        finally:
            self._close_db()


    def import_csv_files(self, table_name):
        try:
            self._connect_db()
            
            csv_files = [f for f in os.listdir(self.export_dir) if f.endswith('.csv') and f.startswith(table_name)]
            if not csv_files:
                print(f"No CSV files found with prefix {table_name}.")
                return
            
            for csv_file in tqdm(csv_files, desc=f"Importing {table_name} CSV file(s)"):
                csv_file_path = os.path.join(self.export_dir, csv_file)
                try:
                    self.conn.execute(f'''
                    INSERT INTO {table_name}
                    SELECT * FROM read_csv_auto('{csv_file_path}')
                    ''')
                except Exception as e:
                    print(f"Failed to import {csv_file}: {e}")
        except Exception as e:
            print(f"An error occurred during the CSV import process: {e}")
        finally:
            self._close_db()

    def check_row_length(self, tablename):
        self._connect_db()
        
        query = f"SELECT COUNT(*) FROM {tablename}"
        result = self.conn.execute(query).fetchone()
        
        self._close_db()
        return result[0]

    def import_all_csv_files(self):
        try:
            self._connect_db()
            self._create_tables()

            tables = ['DataEntry', 'DimNaics', 'DimYear', 'DimZipCode']
            for table_name in tables:
                try:
                    self.import_csv_files(table_name)
                except Exception as e:
                    print(f"An error occurred while importing CSV files for {table_name}: {e}")

        except Exception as e:
            print(f"An error occurred during the import process: {e}")
        finally:
            self._close_db()

    def get_schema(self):
        self._connect_db()

        schema = {}
        tables = self.conn.execute("SHOW TABLES").fetchall()

        for table in tables:
            table_name = table[0]
            columns = self.conn.execute(f"PRAGMA table_info({table_name})").fetchall()
            schema[table_name] = [(col[1], col[2]) for col in columns]  # (column_name, data_type)

        self._close_db()
        return schema

    def check_database_exists(self):
        return os.path.exists(self.db_path)

    def check_csv_files_exist(self, prefix):
        csv_files = [f for f in os.listdir(self.export_dir) if f.endswith('.csv') and f.startswith(prefix)]
        return bool(csv_files)

