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
    Agente de Resumo de Relatório: gera sumários e resumo executivo a partir dos resultados dos agentes de métricas, visualização e notícias.
    Pode ser usado como nó em um grafo LangGraph ou isoladamente.
    """
    def __init__(self):
        pass

    def run(self, metrics: dict, news_analysis: dict, charts: dict, save_json: bool = False) -> dict:
        """
        Gera summary_metrics, summary_charts e executive_summary.
        Se save_json=True, salva o relatório em reports/srag_report_<data>.json
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
    Salva o relatório como JSON na pasta reports e retorna o caminho do arquivo.
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
    Executa o agente de resumo de relatório e retorna os resultados.
    Se save_json=True, salva o relatório em reports/.
    """
    agent = ReportSummaryAgent()
    return agent.run(metrics, news_analysis, charts, save_json=save_json)


if __name__ == "__main__":
    # Exemplo de uso (substitua pelos resultados reais dos outros agentes)
    metrics = {"case_increase_rate": {}, "mortality_rate": {}, "uti_occupancy_rate": {}, "vaccination_rate": {}}
    news_analysis = {"summary": "", "articles": []}
    charts = {"daily_cases_chart": {}, "monthly_cases_chart": {}}
    output = run_report_summary_agent(metrics, news_analysis, charts, save_json=True)
    print("Resultado do ReportSummaryAgent:\n", output)
