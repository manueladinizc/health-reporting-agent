from src.tools.metrics_tools import MetricsTool

class MetricsAgent:
    """
    Metrics Agent: calculates all main metrics using MetricsTool.
    Can be used as a node in a LangGraph or standalone.
    """
    def __init__(self, db_path: str = "src/database.db"):
        self.metrics_tool = MetricsTool(db_path)

    def run(self) -> dict:
        """
        Calculates all metrics and returns a standardized dictionary.
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
    Runs the metrics agent and returns the results.
    """
    agent = MetricsAgent(db_path)
    return agent.run()
