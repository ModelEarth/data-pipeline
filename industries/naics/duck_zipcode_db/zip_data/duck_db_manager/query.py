import os
import duckdb
import csv
import pandas as pd

class DataQueryManager:
    def __init__(self, db_path, export_dir):
        self.db_path = db_path
        self.export_dir = export_dir

    def _connect_db(self):
        return duckdb.connect(self.db_path)

    def execute_query(self, query):
        with self._connect_db() as conn:
            result = conn.execute(query)
            return result.fetchdf()

    def filter(self, zipcode, year=None, industry_level=None, conn=None):
        if not zipcode or not zipcode.isdigit() or len(zipcode) != 5:
            raise ValueError("Zip code must be exactly 5 digits long and is required.")
        
        conditions = [f"SUBSTR(GeoID, 1, 5) = '{zipcode}'"]
        if year:
            conditions.append(f"Year = {year}")
        if industry_level:
            conditions.append(f"IndustryLevel = {industry_level}")

        query = "SELECT GeoID AS Zipcode,NaicsCode,Establishments,Employees,Payroll FROM DataEntry WHERE " + " AND ".join(conditions)
        
        if conn is None:
            with duckdb.connect(self.db_path) as conn:
                return conn.execute(query).fetchdf()
        else:
            return conn.execute(query).fetchdf()