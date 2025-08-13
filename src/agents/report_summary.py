from src.tools.report_summary_tools import (
    generate_summary_metrics,
    generate_summary_charts,
    generate_executive_summary
)
import json
from datetime import datetime
from pathlib import Path

class ReportSummaryAgent:
    """
    Report Summary Agent: generates summaries and executive summary from the results of the metrics, visualization, and news agents.
    Can be used as a node in a LangGraph or standalone.
    """
    def __init__(self):
        pass

    def run(self, metrics: dict, news_analysis: dict, charts: dict, save_json: bool = False) -> dict:
        """
        Generates summary_metrics, summary_charts, and executive_summary.
        If save_json=True, saves the report in reports/srag_report_<date>.json
        """
        summary_metrics = generate_summary_metrics(metrics, news_analysis)
        summary_charts = generate_summary_charts(news_analysis, charts)
        executive_summary = generate_executive_summary(summary_metrics, summary_charts)
        report = {
            "report_metadata": {
                "generation_date": datetime.now().isoformat(),
                "report_type": "SRAG Report",
                "generated_by": "SRAG Report Agent System"
            },
            "metrics": metrics,
            "news_analysis": news_analysis,
            "charts": charts,
            "summary_metrics": summary_metrics,
            "summary_charts": summary_charts,
            "executive_summary": executive_summary
        }
        if save_json:
            report_path = save_report_json(report)
            report["report_path"] = report_path
        return report

def save_report_json(report: dict) -> str:
    """
    Saves the report as JSON in the reports folder and returns the file path.
    """
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    filename = f"srag_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_path = reports_dir / filename
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False, default=str)
    return str(report_path)


def run_report_summary_agent(metrics: dict, news_analysis: dict, charts: dict, save_json: bool = False) -> dict:
    """
    Runs the report summary agent and returns the results.
    If save_json=True, saves the report in reports/.
    """
    agent = ReportSummaryAgent()
    return agent.run(metrics, news_analysis, charts, save_json=save_json)
