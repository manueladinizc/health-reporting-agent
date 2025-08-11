import sqlite3
import pandas as pd
from typing import Dict, Any
from datetime import datetime
from dateutil.relativedelta import relativedelta

from src.utils.logs import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)

class MetricsTool:
    """Tool to consult the SQLite database."""

    def __init__(self, db_path: str = "src/database.db"):
        self.db_path = db_path
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """Executes a SQL query and returns a DataFrame."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query(query, conn)
                logger.info(f"Query executed successfully. Returned {len(df)} rows.")
                return df
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            return pd.DataFrame()



    def get_case_increase_rate(self) -> Dict[str, Any]:
        """
        Calculates the percentage increase in case counts between the penultimate and antepenultimate months in the database.
        The most recent month is always excluded from the calculation, as it may contain incomplete data.
        The method ensures at least three months of data are available, and returns the growth rate, the months compared, and their respective case counts.
        """
        query = """
        with available_months as (
            select distinct ano, mes
            from srag_table
            order by ano desc, mes desc
            limit 3
        ),
        recent_month_cases as (
            select s.ano, s.mes, count(*) as cases
            from srag_table s
            join available_months am on s.ano = am.ano and s.mes = am.mes
            group by s.ano, s.mes
            order by s.ano desc, s.mes desc
        )
        select * from recent_month_cases;
        """

        df = self.execute_query(query)
        if df.empty or len(df) < 3:
            return {"Error": "Insufficient data to calculate rate between penultimate and antepenultimate months."}

        # Sort from most recent to oldest (year, month descending)
        df = df.sort_values(by=["ano", "mes"], ascending=False).reset_index(drop=True)

        # Discard the most recent month (row 0) and reset the index
        df = df.iloc[1:].reset_index(drop=True)  # now rows 0 and 1 are penultimate and antepenultimate months

        cases_penultimate_month = int(df.loc[0, 'cases'])
        penultimate_month = f"{df.loc[0, 'ano']}-{df.loc[0, 'mes']:02d}"

        cases_antepenultimate_month = int(df.loc[1, 'cases'])
        antepenultimate_month = f"{df.loc[1, 'ano']}-{df.loc[1, 'mes']:02d}"

        if cases_antepenultimate_month == 0:
            growth_rate = None
        else:
            growth_rate = ((cases_penultimate_month - cases_antepenultimate_month) / cases_antepenultimate_month) * 100

        return {
            "growth_rate_percent": round(growth_rate, 2) if growth_rate is not None else None,
            "penultimate_month": penultimate_month,
            "cases_penultimate_month": cases_penultimate_month,
            "antepenultimate_month": antepenultimate_month,
            "cases_antepenultimate_month": cases_antepenultimate_month,
            "months_analyzed": len(df)
        }
