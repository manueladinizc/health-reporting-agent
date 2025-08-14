import logging
import asyncio
import os
from pathlib import Path

from langgraph.graph import StateGraph, END

from src.agents.metrics import MetricsAgent
from src.agents.visualization import VisualizationAgent
from src.agents.news_search import NewsSearchAgent
from src.agents.report_summary import run_report_summary_agent
from src.utils.report_render import render_html_report, save_html_report, get_latest_report_json, load_report_data
from src.utils.pdf_render import generate_pdf
from src.data_loader import load_data, SQLITE_DB

logger = logging.getLogger("health_graph")


def node_prepare_database(state):
    """Ensures the SQLite database exists and is populated."""
    logger.info("=== STEP 1: DATABASE SETUP ===")
    if not os.path.exists(SQLITE_DB):
        logger.info(f"Database not found at {SQLITE_DB}. Creating database...")
        load_data()
        logger.info("Database created.")
    else:
        logger.info(f"Database already exists at {SQLITE_DB}.")
    return state

def node_metrics(state):
    """Calculates epidemiological metrics."""
    logger.info("=== STEP 2: METRICS CALCULATION ===")
    try:
        agent = MetricsAgent()
        metrics = agent.run()
        state["metrics"] = metrics
        logger.info("Metrics calculated successfully.")
    except Exception as e:
        logger.error(f"Error calculating metrics: {e}")
        state["metrics"] = {}
    return state

def node_visualization(state):
    """Generates charts and visualizations."""
    logger.info("=== STEP 3: CHARTS GENERATION ===")
    try:
        agent = VisualizationAgent()
        charts = agent.run()
        state["charts"] = charts
        logger.info("Charts generated successfully.")
    except Exception as e:
        logger.error(f"Error generating charts: {e}")
        state["charts"] = {}
    return state

def node_news(state):
    """Fetches and analyzes news data."""
    logger.info("=== STEP 4: NEWS FETCHING & ANALYSIS ===")
    try:
        agent = NewsSearchAgent()
        news = agent.run()
        state["news_analysis"] = news
        logger.info("News fetched successfully.")
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        state["news_analysis"] = {}
    return state

def node_report_summary(state):
    """Generates and saves the report summary."""
    logger.info("=== STEP 5: REPORT SUMMARY GENERATION ===")
    try:
        report = run_report_summary_agent(
            metrics=state.get("metrics", {}),
            news_analysis=state.get("news_analysis", {}),
            charts=state.get("charts", {}),
            save_json=True
        )
        state["report"] = report
        logger.info("Report summary generated and saved successfully.")
    except Exception as e:
        logger.error(f"Error generating report summary: {e}")
        state["report"] = {}
    return state

def node_render_html(state):
    """Renders and saves the HTML report."""
    logger.info("=== STEP 6: HTML REPORT RENDERING ===")
    try:
        json_path = state["report"].get("report_path") or get_latest_report_json()
        data = load_report_data(json_path)
        html = render_html_report(data)
        save_html_report(html)
        logger.info("HTML report rendered and saved successfully.")
    except Exception as e:
        logger.error(f"Error rendering HTML: {e}")
    return state

def node_generate_pdf(state):
    """Generates the PDF report from the HTML file."""
    logger.info("=== STEP 7: PDF GENERATION ===")
    try:
        html_path = Path(__file__).parent.parent / 'resources' / 'reports' / 'srag_report.html'
        pdf_path = Path(__file__).parent.parent / 'resources' / 'reports' / 'srag_report.pdf'
        if html_path.exists():
            asyncio.run(generate_pdf(str(html_path), str(pdf_path)))
            logger.info("PDF generated successfully at /resources/srag_report.pdf.")
        else:
            logger.error(f"HTML file not found: {html_path}")
    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
    return state



def create_graph():
    """Creates and returns the LangGraph pipeline for the health reporting agent."""
    graph = StateGraph(None)
    # Add nodes
    graph.add_node("prepare_database", node_prepare_database)
    graph.add_node("metrics", node_metrics)
    graph.add_node("visualization", node_visualization)
    graph.add_node("news", node_news)
    graph.add_node("report_summary", node_report_summary)
    graph.add_node("render_html", node_render_html)
    graph.add_node("generate_pdf", node_generate_pdf)
    # Add edges
    graph.add_edge("prepare_database", "metrics")
    graph.add_edge("metrics", "visualization")
    graph.add_edge("visualization", "news")
    graph.add_edge("news", "report_summary")
    graph.add_edge("report_summary", "render_html")
    graph.add_edge("render_html", "generate_pdf")
    graph.add_edge("generate_pdf", END)
    graph.set_entry_point("prepare_database")
    return graph



def run_graph():
    """Runs the full srag reporting pipeline graph."""
    state = {}
    graph = create_graph()
    compiled_graph = graph.compile()
    result = compiled_graph.invoke(state)
    return result