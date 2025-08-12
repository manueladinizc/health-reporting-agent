import logging
from src.agents.metrics import MetricsAgent
from src.agents.visualization import VisualizationAgent
from src.agents.news_search import NewsSearchAgent
from src.agents.report_summary import run_report_summary_agent
from src.utils.report_render import render_html_report, save_html_report, get_latest_report_json, load_report_data
from langgraph.graph import StateGraph, END

logger = logging.getLogger("health_graph")



def node_metrics(state):
    try:
        agent = MetricsAgent()
        metrics = agent.run()
        state["metrics"] = metrics
        logger.info("Métricas calculadas com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao calcular métricas: {e}")
        state["metrics"] = {}
    return state

def node_visualization(state):
    try:
        agent = VisualizationAgent()
        charts = agent.run()
        state["charts"] = charts
        logger.info("Gráficos gerados com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao gerar gráficos: {e}")
        state["charts"] = {}
    return state

def node_news(state):
    try:
        agent = NewsSearchAgent()
        news = agent.run()
        state["news_analysis"] = news
        logger.info("Notícias buscadas com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao buscar notícias: {e}")
        state["news_analysis"] = {}
    return state

def node_report_summary(state):
    try:
        report = run_report_summary_agent(
            metrics=state.get("metrics", {}),
            news_analysis=state.get("news_analysis", {}),
            charts=state.get("charts", {}),
            save_json=True
        )
        state["report"] = report
        logger.info("Resumo do relatório gerado e salvo com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao gerar resumo do relatório: {e}")
        state["report"] = {}
    return state

def node_render_html(state):
    try:
        json_path = state["report"].get("report_path") or get_latest_report_json()
        data = load_report_data(json_path)
        html = render_html_report(data)
        save_html_report(html)
        logger.info("Relatório HTML renderizado e salvo com sucesso.")
    except Exception as e:
        logger.error(f"Erro ao renderizar HTML: {e}")
    return state




def create_graph():
    graph = StateGraph(None)
    graph.add_node("metrics", node_metrics)
    graph.add_node("visualization", node_visualization)
    graph.add_node("news", node_news)
    graph.add_node("report_summary", node_report_summary)
    graph.add_node("render_html", node_render_html)

    graph.add_edge("metrics", "visualization")
    graph.add_edge("visualization", "news")
    graph.add_edge("news", "report_summary")
    graph.add_edge("report_summary", "render_html")
    graph.add_edge("render_html", END)

    graph.set_entry_point("metrics")
    return graph

def run_graph():
    state = {}
    graph = create_graph()
    compiled_graph = graph.compile()
    result = compiled_graph.invoke(state)
    return result

if __name__ == "__main__":
    run_graph()
    print("Pipeline completo! Relatório JSON e HTML gerados em /reports.")
