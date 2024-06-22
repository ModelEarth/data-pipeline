import sqlite3
import pandas as pd
class DatabaseManager:
    def __init__(self, db_path='./zip_data/us_economic_data.db'):
        self.db_path = db_path
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self._create_tables()
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        
    def open(self):
        if not self.conn:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            self._create_tables()

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None

    def insert_data_entries(self, data_rows):
        try:
            self.cursor.executemany('''
                INSERT INTO DataEntry (GeoID, NaicsCode, Year, Establishments, Employees, Payroll, IndustryLevel) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', data_rows)
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            self.conn.rollback()
    
    def data_for_year_and_sector_exists(self, year, sector):
        query = '''
            SELECT EXISTS(
                SELECT 1 FROM DataEntry WHERE Year = ? AND NaicsCode = ?
            )
        '''
        self.cursor.execute(query, (year, sector))
        return self.cursor.fetchone()[0] == 1



    def data_exists(self, table_name):
        """ Check if data exists in a given table. """
        self.cursor.execute(f"SELECT EXISTS(SELECT 1 FROM {table_name} LIMIT 1)")
        return self.cursor.fetchone()[0] == 1

    def _create_tables(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS DataEntry (
                EntryID INTEGER PRIMARY KEY AUTOINCREMENT,
                GeoID VARCHAR,  
                NaicsCode VARCHAR,  
                Year INTEGER,  
                Establishments INTEGER,
                Employees INTEGER,
                Payroll INTEGER,
                IndustryLevel INT
            )
        ''')
        self.conn.commit()
        self._create_indexes()


    def _create_indexes(self):
        # Create indexes on frequently queried columns to improve query performance
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_geo_id ON DataEntry(GeoID);
        ''')
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_naics_code ON DataEntry(NaicsCode);
        ''')




