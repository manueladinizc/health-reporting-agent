import os
import sys
from pathlib import Path
import logging

sys.path.append(str(Path(__file__).parent / "src"))

from data_loader import load_multiple_from_urls, save_to_sqlite, CSV_URLS, SQLITE_DB, TABLE_NAME
from utils.logs import setup_logging
from graph_workflow import run_graph

setup_logging()

logger = logging.getLogger(__name__)


def prepare_database():
	"""
	Checks if the SQLite database exists, and creates it if not.
	"""
	logger.info("=== STEP 1: DATABASE SETUP ===")
	if not os.path.exists(SQLITE_DB):
		logger.info(f"Database not found at {SQLITE_DB}. Creating database...")
		df_final = load_multiple_from_urls(CSV_URLS)
		save_to_sqlite(df_final, SQLITE_DB, TABLE_NAME)
		logger.info("Database created.")
	else:
		logger.info(f"Database already exists at {SQLITE_DB}.")

if __name__ == "__main__":
	logger.info("Iniciando pipeline de geração de relatório SRAG...")
	prepare_database()
	run_graph()
	logger.info("Pipeline finalizado! Relatório JSON e HTML gerados em /reports.")
