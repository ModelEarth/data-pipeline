import os
import logging
import duckdb
from multiprocessing import Pool
from tqdm import tqdm
from itertools import repeat

class DataExporter:
    def __init__(self, export_dir, db_path, threads=4):
        self.export_dir = export_dir
        os.makedirs(self.export_dir, exist_ok=True)
        self.db_path = db_path
        self.threads = threads
        logging.basicConfig(level=logging.INFO)

    def _fetch_geo_ids(self):
        with duckdb.connect(self.db_path, read_only=True) as conn:
            return conn.execute("SELECT DISTINCT GeoID FROM DataEntry").fetchall()

    def _export_geo_data(self, args):
        geo_id, geo_path = args
        nested_path = os.path.join(geo_path, *list(geo_id))
        os.makedirs(nested_path, exist_ok=True)
        with duckdb.connect(self.db_path, read_only=True) as conn:
            combinations = conn.execute(f"SELECT DISTINCT Year, IndustryLevel FROM DataEntry WHERE GeoID = '{geo_id}'").fetchall()
            for year, industry_level in combinations:
                chunk_file_path = os.path.join(nested_path, f"data_{year}_{industry_level}.csv")
                if os.path.exists(chunk_file_path):
                    logging.info(f"Skipping existing file: {chunk_file_path}")
                    continue
                query = f"""
                    COPY (
                        SELECT GeoID,NaicsCode,Establishments,Employees,Payroll FROM DataEntry WHERE GeoID = '{geo_id}' AND Year = {year} AND IndustryLevel = '{industry_level}'
                    ) TO '{chunk_file_path}' WITH (FORMAT CSV, HEADER)
                """
                conn.execute(query)

    def _export_geo_data_for_year(self, args):
        geo_id, geo_path, year = args
        nested_path = os.path.join(geo_path, *list(geo_id))
        os.makedirs(nested_path, exist_ok=True)
        with duckdb.connect(self.db_path, read_only=True) as conn:
            combinations = conn.execute(f"SELECT DISTINCT IndustryLevel FROM DataEntry WHERE GeoID = '{geo_id}' AND Year = {year}").fetchall()
            for industry_level in combinations:
                chunk_file_path = os.path.join(nested_path, f"data_{year}_{industry_level}.csv")
                if os.path.exists(chunk_file_path):
                    logging.info(f"Skipping existing file: {chunk_file_path}")
                    continue
                query = f"""
                    COPY (
                        SELECT GeoID,NaicsCode,Establishments,Employees,Payroll FROM DataEntry WHERE GeoID = '{geo_id}' AND Year = {year} AND IndustryLevel = '{industry_level}'
                    ) TO '{chunk_file_path}' WITH (FORMAT CSV, HEADER)
                """
                conn.execute(query)

    def export_geo_nested_csv(self):
        geo_ids = self._fetch_geo_ids()
        tasks = [(geo_id, self.export_dir) for geo_id, in geo_ids]

        with Pool(processes=self.threads) as pool:
            list(tqdm(pool.imap_unordered(self._export_geo_data, tasks), total=len(tasks), desc="Processing GeoIDs"))

    def export_geo_nested_csv_for_year(self, year):
        geo_ids = self._fetch_geo_ids()
        tasks = [(geo_id, self.export_dir, year) for geo_id, in geo_ids]

        with Pool(processes=self.threads) as pool:
            list(tqdm(pool.imap_unordered(self._export_geo_data_for_year, tasks), total=len(tasks), desc=f"Processing GeoIDs for Year {year}"))
