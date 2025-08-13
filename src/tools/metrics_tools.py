import sqlite3
import pandas as pd
from typing import Dict, Any
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



    def get_month_case_increase_rate(self) -> Dict[str, Any]:
        """
        Calculate the percentage increase in case counts between the last two complete months.

        Ignores the most recent month (which may be incomplete).

        Returns:
            dict: {
                "current_month": (year, month),
                "latest_cases": int,
                "compared_month": (year, month),
                "previous_cases": int,
                "percent_increase_rate": float or None
            }
        """
        query = """
        with cases_per_month as (
            select
                ano as year,
                mes as month,
                count(*) as total_cases
            from srag_table
            group by ano, mes
        ),
        ordered as (
            select *
            from cases_per_month
            order by year desc, month desc
        )
        select *
        from ordered
        limit -1 offset 1;
        """

        df = self.execute_query(query)

        if df.empty or len(df) < 2:
            logger.warning("Insufficient data to calculate the increase rate.")
            return {}

        df = df.sort_values(by=["year", "month"], ascending=False).head(2)

        latest_cases = df.iloc[0]["total_cases"]
        previous_cases = df.iloc[1]["total_cases"]

        if previous_cases == 0:
            logger.warning("Previous month has zero cases, cannot calculate rate.")
            percent_increase_rate = None
        else:
            percent_increase_rate = ((latest_cases - previous_cases) / previous_cases) * 100

        result = {
            "current_month": (int(df.iloc[0]["year"]), int(df.iloc[0]["month"])),
            "latest_cases": int(latest_cases),
            "compared_month": (int(df.iloc[1]["year"]), int(df.iloc[1]["month"])),
            "previous_cases": int(previous_cases),
            "percent_increase_rate": percent_increase_rate
        }

        logger.info(f"Increase rate calculated: {percent_increase_rate:.4f}")
        return result

    def get_month_mortality_rate(self) -> Dict[str, Any]:
        """
        Calculate the mortality rate (EVOLUCAO = 2) for the last complete month.

        Ignores the most recent month (which may be incomplete).

        Returns:
            dict: {
                "year": int,
                "month": int,
                "total_cases": int,
                "total_deaths": int,
                "mortality_rate": float or None
            }
        """
        query = """
        with cases_per_month as (
            select
                ano as year,
                mes as month,
                count(*) as total_cases,
                sum(case when evolucao = 2 then 1 else 0 end) as total_deaths
            from srag_table
            group by ano, mes
        ),
        ordered as (
            select *
            from cases_per_month
            order by year desc, month desc
        )
        select *
        from ordered
        limit 1 offset 1;
        """

        df = self.execute_query(query)

        if df.empty:
            logger.warning("Insufficient data to calculate the mortality rate for the last complete month.")
            return {}

        row = df.iloc[0]
        total_cases = row["total_cases"]
        total_deaths = row["total_deaths"]

        mortality_rate = ((total_deaths / total_cases) * 100) if total_cases > 0 else None

        result = {
            "year": int(row["year"]),
            "month": int(row["month"]),
            "total_cases": int(total_cases),
            "total_deaths": int(total_deaths),
            "mortality_rate": mortality_rate
        }

        logger.info(f"Mortality rate for the last complete month ({result['year']}-{result['month']}): {mortality_rate}")
        return result

    def get_month_uti_occupancy_rate(self) -> Dict[str, Any]:
        """
        Calculate the ICU (UTI) occupancy rate for the last complete month.

        Ignores the most recent month (which may be incomplete).

        Returns:
            dict: {
                "year": int,
                "month": int,
                "total_cases": int,
                "total_uti_cases": int,
                "uti_occupancy_rate_percent": float or None
            }
        """
        query = """
        with cases_per_month as (
            select
                ano as year,
                mes as month,
                count(*) as total_cases,
                sum(case when uti = 1 then 1 else 0 end) as total_uti_cases
            from srag_table
            group by ano, mes
        ),
        ordered as (
            select *
            from cases_per_month
            order by year desc, month desc
        )
        select *
        from ordered
        limit 1 offset 1;
        """

        df = self.execute_query(query)

        if df.empty:
            logger.warning("Insufficient data to calculate the ICU occupancy rate for the last complete month.")
            return {}

        row = df.iloc[0]
        total_cases = row["total_cases"]
        total_uti_cases = row["total_uti_cases"]

        occupancy_rate = (total_uti_cases / total_cases * 100) if total_cases > 0 else None

        result = {
            "year": int(row["year"]),
            "month": int(row["month"]),
            "total_cases": int(total_cases),
            "total_uti_cases": int(total_uti_cases),
            "uti_occupancy_rate_percent": round(occupancy_rate, 2) if occupancy_rate is not None else None
        }

        logger.info(f"UTI occupancy rate for the last complete month ({result['year']}-{result['month']}): {result['uti_occupancy_rate_percent']}%")
        return result

    def get_month_covid_vaccination_rate(self) -> Dict[str, Any]:
        """
        Calculate the COVID vaccination rate (VACINA_COV = 1) for the last complete month.

        Ignores the most recent month (which may be incomplete).

        Returns:
            dict: {
                "year": int,
                "month": int,
                "total_cases": int,
                "total_vaccinated": int,
                "covid_vaccination_rate_percent": float or None
            }
        """
        query = """
        with cases_per_month as (
            select
                ano as year,
                mes as month,
                count(*) as total_cases,
                sum(case when vacina_cov = 1 then 1 else 0 end) as total_vaccinated
            from srag_table
            group by ano, mes
        ),
        ordered as (
            select *
            from cases_per_month
            order by year desc, month desc
        )
        select *
        from ordered
        limit 1 offset 1;
        """

        df = self.execute_query(query)

        if df.empty:
            logger.warning("Insufficient data to calculate the COVID vaccination rate for the last complete month.")
            return {}

        row = df.iloc[0]
        total_cases = row["total_cases"]
        total_vaccinated = row["total_vaccinated"]

        vaccination_rate = (total_vaccinated / total_cases * 100) if total_cases > 0 else None

        result = {
            "year": int(row["year"]),
            "month": int(row["month"]),
            "total_cases": int(total_cases),
            "total_vaccinated": int(total_vaccinated),
            "covid_vaccination_rate_percent": round(vaccination_rate, 2) if vaccination_rate is not None else None
        }

        logger.info(f"COVID vaccination rate for the last complete month ({result['year']}-{result['month']}): {result['covid_vaccination_rate_percent']}%")
        return result
