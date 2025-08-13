from src.tools.visualization_tools import VisualizationTool

class VisualizationAgent:
    """
    Visualization Agent: generates daily and monthly charts using VisualizationTool.
    Can be used as a node in a LangGraph or standalone.
    """
    def __init__(self, db_path: str = "src/database.db"):
        self.visualization_tool = VisualizationTool(db_path)

    def run(self, days: int = 30, months: int = 12) -> dict:
        """
        Generates the main charts and returns a dictionary with the results.
        """
        daily_chart = self.visualization_tool.create_daily_cases_chart(days=days)
        monthly_chart = self.visualization_tool.create_monthly_cases_chart(months=months)
        return {
            "daily_cases_chart": daily_chart,
            "monthly_cases_chart": monthly_chart
        }


def run_visualization_agent(db_path: str = "src/database.db", days: int = 30, months: int = 12) -> dict:
    """
    Runs the visualization agent and returns the results.
    """
    agent = VisualizationAgent(db_path)
    return agent.run(days=days, months=months)