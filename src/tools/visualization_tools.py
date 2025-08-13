import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import logging
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class VisualizationTool:
    """Ferramenta para gerar gráficos e visualizações a partir dos dados."""

    def __init__(self, db_path: str = "src/database.db"):
        self.db_path = db_path
        self.output_dir = Path("reports/charts")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._setup_style()

    def _setup_style(self):
        """Configura o estilo padrão para os gráficos do Seaborn."""
        self.sns_style = "darkgrid"
        self.sns_style_params = {"grid.color": ".5", "grid.linestyle": ":"}
        self.colors = ["#001F3F", "#AAAAAA", "#334C66", "#7099A8", "#D8D8D8"]
        sns.set_style(self.sns_style, self.sns_style_params)
        sns.set_palette(sns.color_palette(self.colors))

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Executa uma consulta SQL parametrizada e retorna um DataFrame.
        Usar parâmetros previne SQL Injection.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query(query, conn, params=params)
                logger.info(f"Query executada com sucesso. Retornou {len(df)} linhas.")
                return df
        except Exception as e:
            logger.error(f"Erro ao executar a query: {e}")
            return pd.DataFrame()

    def _save_and_close_plot(self, fig, filename: str) -> Path:
        """Salva a figura do gráfico e a fecha para liberar memória."""
        output_path = self.output_dir / filename
        plt.tight_layout()
        fig.savefig(output_path)
        plt.close(fig)
        logger.info(f"Gráfico salvo em: {output_path}")
        return output_path

    def create_daily_cases_chart(self, days: int = 30) -> Dict[str, Any]:
        """
        Gera um gráfico de casos diários para os N dias que antecedem o
        último mês completo com dados.
        """
        logger.info(f"Iniciando gráfico de casos diários dos últimos {days} dias.")
        
        # A query agora faz todo o trabalho de cálculo de datas,
        # eliminando a necessidade de uma consulta preliminar.
        query = """
            WITH MaxDate AS (
                SELECT MAX(DT_SIN_PRI_DATETIME) as value FROM srag_table
            ),
            EndDate AS (
                SELECT DATE((SELECT value FROM MaxDate), 'start of month', '-1 day') as value
            ),
            StartDate AS (
                SELECT DATE((SELECT value FROM EndDate), :days_interval) as value
            )
            SELECT
                DATE(DT_SIN_PRI_DATETIME) as date,
                COUNT(*) as cases
            FROM srag_table
            WHERE DT_SIN_PRI_DATETIME BETWEEN (SELECT value FROM StartDate) AND (SELECT value FROM EndDate)
            GROUP BY date
            ORDER BY date;
        """
        
        # Usamos parâmetros para segurança e clareza
        params = {"days_interval": f"-{days - 1} days"}
        df = self.execute_query(query, params=params)

        if df.empty or len(df) < 2:
            logger.warning("Dados insuficientes para gerar o gráfico de casos diários.")
            return {"error": "Dados insuficientes para gerar o gráfico."}

        df['date'] = pd.to_datetime(df['date'])

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(df['date'], df['cases'], color=self.colors[0], alpha=0.9, label='Casos Diários')

        if len(df) >= 7:
            df['media_movel'] = df['cases'].rolling(window=7, min_periods=1).mean()
            ax.plot(df['date'], df['media_movel'], color='gray', linewidth=2, label='Média Móvel (7 dias)')
            logger.info("Média móvel de 7 dias adicionada.")

        ax.set_xlabel("Data")
        ax.set_ylabel("Número de Casos")
        plt.xticks(rotation=45, ha='right')
        ax.legend()
        
        output_path = self._save_and_close_plot(fig, "daily_cases.png")
        
        df['date'] = df['date'].dt.strftime('%Y-%m-%d')
        data_list = df[['date', 'cases']].to_dict(orient='records')
        description = (
            f"Casos diários dos {days} dias anteriores ao último mês completo.\n"
            f"Período de {data_list[0]['date']} a {data_list[-1]['date']}."
        )

        return {"image_path": str(output_path), "data": data_list, "description": description}


    def create_monthly_cases_chart(self, months: int = 12) -> Dict[str, Any]:
        """
        Gera um gráfico de casos mensais para os últimos N meses completos.
        """
        logger.info(f"Iniciando gráfico de casos mensais dos últimos {months} meses.")
        
        # Query simplificada para buscar todos os meses completos e depois filtrar os últimos N
        query = """
            SELECT
                STRFTIME('%Y-%m', DT_SIN_PRI_DATETIME) as month_year,
                COUNT(*) as cases
            FROM srag_table
            WHERE DT_SIN_PRI_DATETIME < DATE((SELECT MAX(DT_SIN_PRI_DATETIME) FROM srag_table), 'start of month')
            GROUP BY month_year
            ORDER BY month_year;
        """
        df_all_months = self.execute_query(query)
        
        if df_all_months.empty or len(df_all_months) < 2:
            logger.warning("Dados insuficientes para gerar o gráfico mensal.")
            return {"error": "Dados insuficientes (mínimo 2 meses completos)."}

        # Filtra os últimos N meses no pandas, o que é mais simples
        df = df_all_months.tail(months).copy()
        
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.barplot(x='month_year', y='cases', data=df, ax=ax, alpha=0.9, color=self.colors[0])
        ax.set_xlabel("Ano-Mês")
        ax.set_ylabel("Número de Casos")
        plt.xticks(rotation=45, ha='right')
        
        output_path = self._save_and_close_plot(fig, "monthly_cases.png")

        data_list = df.to_dict(orient='records')
        description = f"Casos mensais para os últimos {len(df)} meses completos."
        
        return {"image_path": str(output_path), "data": data_list, "description": description}