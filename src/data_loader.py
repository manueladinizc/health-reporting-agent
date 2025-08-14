import os
import time
import logging
import concurrent.futures
from typing import List

import pandas as pd
from sqlalchemy import create_engine

logger = logging.getLogger(__name__)

# Project configuration
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
SQLITE_DB = os.path.join(PROJECT_ROOT, "src", "database.db")
TABLE_NAME = "srag_table"

# Dataset configuration
COLUMNS = [
    'DT_SIN_PRI', 'EVOLUCAO', 'UTI', 'VACINA_COV',
    'VACINA', 'CLASSI_FIN', 'SEM_PRI'
]

EXPECTED_FILES = [
    "INFLUD25-08-08-2025.csv",
    "INFLUD24-26-06-2025.csv"
]

CSV_URLS = [
    "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SRAG/2025/INFLUD25-04-08-2025.csv",
    "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SRAG/2024/INFLUD24-26-06-2025.csv"
]


def process_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Apply standard processing to loaded data."""
    df = df.fillna(9)
    dt_temp = pd.to_datetime(df['DT_SIN_PRI'], format='%Y-%m-%d', errors='coerce')

    df['ANO'] = dt_temp.dt.year
    df['MES'] = dt_temp.dt.month
    df['ANO-SEMANA'] = dt_temp.dt.strftime('%Y') + '-' + dt_temp.dt.isocalendar().week.astype(str).str.zfill(2)
    df['ANO-MES'] = dt_temp.dt.strftime('%Y-%m')
    df['DT_SIN_PRI_DATETIME'] = dt_temp.dt.date

    return df


def load_csv(source: str, local: bool) -> pd.DataFrame:
    """Load CSV from local file or URL, applying processing."""
    origin = "local" if local else "URL"
    logger.info(f"Loading from {origin}: {source}")
    start = time.time()

    df = pd.read_csv(
        source,
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

    df = process_dataframe(df)

    elapsed = time.time() - start
    logger.info(f"{os.path.basename(source) if local else source.split('/')[-1]}: "
                f"{len(df)} rows loaded in {elapsed:.2f}s")
    return df


def load_multiple(sources: List[str], from_local: bool) -> pd.DataFrame:
    """Load multiple CSVs in parallel and concatenate them."""
    start = time.time()
    logger.info("Loading datasets in parallel...")

    dataframes = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(4, len(sources))) as executor:
        futures = [executor.submit(load_csv, s, from_local) for s in sources]
        for future in concurrent.futures.as_completed(futures):
            try:
                dataframes.append(future.result())
            except Exception as e:
                logger.error(f"Error loading dataset: {e}")

    if not dataframes:
        raise RuntimeError("No datasets were loaded.")

    df_final = pd.concat(dataframes, ignore_index=True)
    logger.info(f"Total: {len(df_final)} rows loaded in {time.time() - start:.2f}s")
    return df_final


def save_to_sqlite(df: pd.DataFrame, db_path: str, table: str):
    """Save DataFrame to SQLite database."""
    logger.info(f"Saving data to {db_path}...")
    start = time.time()

    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    df.to_sql(table, con=engine, index=False, if_exists="replace", chunksize=10000, method="multi")

    logger.info(f"Database saved in {time.time() - start:.2f}s")


def get_data_sources() -> (List[str], bool):
    """
    Returns a list of sources and whether they are local or URLs.
    Prioritizes local files if all exist.
    """
    local_paths = [os.path.join(DATA_DIR, f) for f in EXPECTED_FILES]
    if all(os.path.isfile(p) for p in local_paths):
        logger.info("Found all expected local CSV files. Using local sources.")
        return local_paths, True
    else:
        logger.info("Local CSV files not found. Using remote URLs.")
        return CSV_URLS, False


def load_data():
    logger.info("Starting data loading process...")
    sources, from_local = get_data_sources()
    logger.info(f"Data sources determined: {sources} (local={from_local})")
    df = load_multiple(sources, from_local)
    logger.info("Saving loaded data to SQLite database...")
    save_to_sqlite(df, SQLITE_DB, TABLE_NAME)
    logger.info("Data loading and saving process completed successfully.")
