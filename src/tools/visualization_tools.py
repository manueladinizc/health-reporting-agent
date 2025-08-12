import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class VisualizationTool:
    """Tool to generate charts and visualizations."""

    def __init__(self, db_path: str = "src/database.db"):
        self.db_path = db_path
        self.output_dir = Path("reports/charts")
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # General configs
        self.sns_style = "darkgrid"
        self.sns_style_params = {"grid.color": ".5", "grid.linestyle": ":"}
        self.colors = ["#001F3F", "#AAAAAA", "#334C66", "#7099A8", "#D8D8D8"]
        self.line_color = self.colors[0]

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

    def _prepare_plot_style(self):
        """Applies the seaborn style and palette."""
        sns.set_style(self.sns_style, self.sns_style_params)
        sns.set_palette(sns.color_palette(self.colors))

    def create_daily_cases_chart(self, days: int = 30) -> dict:
        """
        Create a daily cases chart for the last N days,
        save as PNG, and return a textual description of the data.
        """
        query = f"""
        SELECT DATE(DT_SIN_PRI_DATETIME) as date, COUNT(*) as cases
        FROM srag_table 
        WHERE DT_SIN_PRI_DATETIME >= date('now', '-{days} days')
        AND DT_SIN_PRI_DATETIME IS NOT NULL
        GROUP BY DATE(DT_SIN_PRI_DATETIME)
        ORDER BY date
        """
        df = self.execute_query(query)
        if df.empty or len(df) < 2:
            return {"error": "Not enough data for the chart (minimum 2 days)"}


        self._prepare_plot_style()

        fig, ax = plt.subplots(figsize=(8, 4))
        sns.lineplot(x='date', y='cases', data=df, marker='o', ax=ax, color=self.line_color)
        ax.collections[0].set_edgecolor(self.line_color)
        ax.set_xlabel("Data")
        ax.set_ylabel("Número de Casos")
        ax.set_title(f"Casos Diários de SRAG - Últimos {days} dias")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        output_path = self.output_dir / "daily_cases.png"
        plt.savefig(output_path)

        logger.info(f"Gráfico de casos diários salvo em: {output_path}")

        data_list = df[['date', 'cases']].to_dict(orient='records')
        description = f"Casos diários dos últimos {days} dias:\n" + \
                      "\n".join([f"- {row['date']}: {row['cases']}" for row in data_list])
        return {"image_path": str(output_path), "data": data_list, "description": description}

    def create_monthly_cases_chart(self, months: int = 12) -> dict:
        """
        Create a monthly cases chart for the last N months (excluding the most recent month),
        save as PNG, and return a textual description of the data.
        """
        query = f"""
        SELECT 
            ANO || '-' || printf('%02d', MES) as month_year,
            COUNT(*) as cases
        FROM srag_table 
        WHERE DT_SIN_PRI_DATETIME >= date('now', '-{months} months')
        AND DT_SIN_PRI_DATETIME IS NOT NULL
        GROUP BY ANO, MES
        ORDER BY ANO, MES
        """
        df = self.execute_query(query)
        if df.empty or len(df) < 2:
            return {"error": "Not enough data for the chart (minimum 2 months)"}
        # Remove the last month
        df = df.iloc[:-1]

        self._prepare_plot_style()

        fig, ax = plt.subplots(figsize=(8, 4))
        sns.barplot(x='month_year', y='cases', data=df, ax=ax)
        ax.set_xlabel("Ano-Mês")
        ax.set_ylabel("Número de Casos")
        ax.set_title(f"Casos Mensais de SRAG - Últimos {months} meses")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        output_path = self.output_dir / "monthly_cases.png"
        plt.savefig(output_path)
        plt.close()
        logger.info(f"Gráfico de casos mensais salvo em: {output_path}")

        data_list = df[['month_year', 'cases']].to_dict(orient='records')
        description = (
            f"Casos mensais dos últimos {months} meses:\n" + \
            "\n".join([f"- {row['month_year']}: {row['cases']} casos" for row in data_list])
        )
        return {"image_path": str(output_path), "data": data_list, "description": description}
