from src.tools.metrics_tools import MetricsTool

class MetricsAgent:
    """
    Agente de Métricas: calcula todas as métricas principais usando MetricsTool.
    Pode ser usado como nó em um grafo LangGraph ou isoladamente.
    """
    def __init__(self, db_path: str = "src/database.db"):
        self.metrics_tool = MetricsTool(db_path)

    def run(self) -> dict:
        """
        Calcula todas as métricas e retorna um dicionário padronizado.
        """
        case_increase_rate = self.metrics_tool.get_month_case_increase_rate()
        mortality_rate = self.metrics_tool.get_month_mortality_rate()
        uti_occupancy_rate = self.metrics_tool.get_month_uti_occupancy_rate()
        vaccination_rate = self.metrics_tool.get_month_covid_vaccination_rate()
        return {
            "case_increase_rate": case_increase_rate,
            "mortality_rate": mortality_rate,
            "uti_occupancy_rate": uti_occupancy_rate,
            "vaccination_rate": vaccination_rate
        }


def run_metrics_agent(db_path: str = "src/database.db") -> dict:
    """
    Executa o agente de métricas e retorna os resultados.
    """
    agent = MetricsAgent(db_path)
    return agent.run()


if __name__ == "__main__":
    output = run_metrics_agent()
    print("Resultado do MetricsAgent:\n", output)
