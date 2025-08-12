from src.tools.visualization_tools import VisualizationTool

class VisualizationAgent:
    """
    Agente de Visualização: gera gráficos diários e mensais usando VisualizationTool.
    Pode ser usado como nó em um grafo LangGraph ou isoladamente.
    """
    def __init__(self, db_path: str = "src/database.db"):
        self.visualization_tool = VisualizationTool(db_path)

    def run(self, days: int = 30, months: int = 12) -> dict:
        """
        Gera os gráficos principais e retorna um dicionário com os resultados.
        """
        daily_chart = self.visualization_tool.create_daily_cases_chart(days=days)
        monthly_chart = self.visualization_tool.create_monthly_cases_chart(months=months)
        return {
            "daily_cases_chart": daily_chart,
            "monthly_cases_chart": monthly_chart
        }


def run_visualization_agent(db_path: str = "src/database.db", days: int = 30, months: int = 12) -> dict:
    """
    Executa o agente de visualização e retorna os resultados.
    """
    agent = VisualizationAgent(db_path)
    return agent.run(days=days, months=months)


if __name__ == "__main__":
    output = run_visualization_agent()
    print("Resultado do VisualizationAgent:\n", output)
