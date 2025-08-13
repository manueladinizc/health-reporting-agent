import logging
from src.utils.logs import setup_logging
from src.graph_workflow import run_graph

setup_logging()

logger = logging.getLogger(__name__)


if __name__ == "__main__":
	logger.info("Starting SRAG report generation pipeline...")
	run_graph()
	logger.info("Pipeline finished! JSON, HTML, and PDF reports generated in /reports.")
