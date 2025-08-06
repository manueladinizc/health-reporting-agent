import pandas as pd
from sqlalchemy import create_engine
import concurrent.futures
import time
from typing import List
from pathlib import Path

# Global configuration
DATA_FILES = [
    Path("data/INFLUD24-26-06-2025.csv"),
    Path("data/INFLUD25-04-08-2025.csv")
]
COLUMNS = ['DT_SIN_PRI', 'EVOLUCAO', 'UTI', 'VACINA_COV', 'VACINA', 'CLASSI_FIN', 'SEM_PRI']
DB_PATH = "src/database.db"
TABLE_NAME = "srag_table"


def load_data(filepath: Path) -> pd.DataFrame:
    """Reads and preprocesses a SRAG CSV file."""
    print(f"Loading: {filepath}")
    start = time.time()
    df = pd.read_csv(
        filepath,
        sep=';',
        usecols=COLUMNS,
        encoding='ISO-8859-1',
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
        na_values=['', 'nan', 'NaN'],
    )
    df = df.fillna(9)
    # Date processing
    dt_temp = pd.to_datetime(df['DT_SIN_PRI'], format='%Y-%m-%d', errors='coerce')
    df['ANO'] = dt_temp.dt.year
    df['MES'] = dt_temp.dt.month
    df['ANO-SEMANA'] = dt_temp.dt.strftime('%Y') + '-' + dt_temp.dt.isocalendar().week.astype(str).str.zfill(2)
    df['ANO-MES'] = dt_temp.dt.strftime('%Y-%m')
    df['DT_SIN_PRI_DATETIME'] = dt_temp.dt.date
    elapsed = time.time() - start
    print(f"{filepath.name}: {len(df)} rows loaded in {elapsed:.2f}s")
    return df


def load_multiple(files: List[Path]) -> pd.DataFrame:
    """Loads multiple files in parallel and concatenates the DataFrames."""
    print("Loading multiple datasets in parallel...")
    start = time.time()
    dataframes = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(4, len(files))) as executor:
        future_to_path = {executor.submit(load_data, path): path for path in files}
        for future in concurrent.futures.as_completed(future_to_path):
            path = future_to_path[future]
            try:
                df = future.result()
                dataframes.append(df)
            except Exception as exc:
                print(f"Error loading {path}: {exc}")
    if not dataframes:
        raise Exception("No datasets were loaded successfully.")
    df_total = pd.concat(dataframes, ignore_index=True)
    elapsed = time.time() - start
    print(f"Total: {len(df_total)} rows in {elapsed:.2f}s")
    return df_total


def check_files(files: List[Path]):
    print("Checking data files...")
    for file_path in files:
        if file_path.exists():
            file_size = file_path.stat().st_size / (1024 * 1024)
            print(f"  Found: {file_path} ({file_size:.1f} MB)")
        else:
            print(f"  File not found: {file_path}")
            raise FileNotFoundError(f"Required file not found: {file_path}")

def save_to_sqlite(df: pd.DataFrame, db_path: str, table: str):
    print(f"Saving to SQLite database: {db_path} ...")
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
    print(f"SQLite database created at: {db_path} ({elapsed:.2f}s)")

if __name__ == "__main__":
    check_files(DATA_FILES)
    df_total = load_multiple(DATA_FILES)
    save_to_sqlite(df_total, DB_PATH, TABLE_NAME)
