import pandas as pd
import time
from sqlalchemy import create_engine
import concurrent.futures
from typing import List
import os
import logging

logger = logging.getLogger(__name__)

# URLs from https://opendatasus.saude.gov.br/dataset/srag-2021-a-2024
CSV_URLS = [
    "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SRAG/2025/INFLUD25-04-08-2025.csv",
    "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SRAG/2024/INFLUD24-26-06-2025.csv"
]

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
SQLITE_DB = os.path.join(PROJECT_ROOT, "src", "database.db")
TABLE_NAME = "srag_table"

# Columns to select
COLUMNS = ['DT_SIN_PRI', 'EVOLUCAO', 'UTI', 'VACINA_COV', 'VACINA', 'CLASSI_FIN', 'SEM_PRI']

def load_data_from_url(url: str) -> pd.DataFrame:
    """Loads and processes data from a URL."""
    logger.info(f"Loading: {url}")
    start = time.time()
    
    df = pd.read_csv(
        url,
        sep=';',
        usecols=COLUMNS,
        encoding='latin1',
        low_memory=False,
        dtype={
            'DT_SIN_PRI': 'string',
            'EVOLUCAO': 'Int64',
            'UTI': 'Int64',
            'VACINA_COV': 'Int64',
            'VACINA': 'Int64',
            'CLASSI_FIN': 'Int64',
            'SEM_PRI': 'Int64'
        },
    )

    # Fill missing values with 9 (In the dictionary, 9 means "Ignored")
    df = df.fillna(9)

    # Data processing
    dt_temp = pd.to_datetime(df['DT_SIN_PRI'], format='%Y-%m-%d', errors='coerce')
    df['ANO'] = dt_temp.dt.year
    df['MES'] = dt_temp.dt.month
    df['ANO-SEMANA'] = dt_temp.dt.strftime('%Y') + '-' + dt_temp.dt.isocalendar().week.astype(str).str.zfill(2)
    df['ANO-MES'] = dt_temp.dt.strftime('%Y-%m')
    df['DT_SIN_PRI_DATETIME'] = dt_temp.dt.date

    elapsed = time.time() - start
    logger.info(f"{url.split('/')[-1]}: {len(df)} rows loaded in {elapsed:.2f}s")
    return df

def load_multiple_from_urls(urls: List[str]) -> pd.DataFrame:
    """Loads multiple CSVs in parallel and concatenates them."""
    logger.info("Loading all datasets in parallel...")
    start = time.time()
    dataframes = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=min(4, len(urls))) as executor:
        future_to_url = {executor.submit(load_data_from_url, url): url for url in urls}
        for future in concurrent.futures.as_completed(future_to_url):
            try:
                df = future.result()
                dataframes.append(df)
            except Exception as exc:
                logger.error(f"Loading error {future_to_url[future]}: {exc}")

    if not dataframes:
        raise Exception("No datasets were loaded.")
    
    df_final = pd.concat(dataframes, ignore_index=True)
    elapsed = time.time() - start
    logger.info(f"Total: {len(df_final)} rows loaded in {elapsed:.2f}s")
    return df_final

def save_to_sqlite(df: pd.DataFrame, db_path: str, table: str):
    """Saves DataFrame to SQLite database."""
    logger.info(f"Saving to database {db_path} ...")
    start = time.time()
    
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    df.to_sql(
        table,
        con=engine,
        index=False,
        if_exists="replace",
        chunksize=10000,
        method='multi'
    )
    
    elapsed = time.time() - start
    logger.info(f"Database created at: {db_path} ({elapsed:.2f}s)")
