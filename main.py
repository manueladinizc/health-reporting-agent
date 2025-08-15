import logging
from src.utils.logs import setup_logging
from src.utils.env_guard import check_required_env_vars
from src.graph_workflow import run_graph

setup_logging()

logger = logging.getLogger(__name__)

# List your required environment variables here
REQUIRED_ENV_VARS = [
	"OPENAI_API_KEY",
	"SERPER_API_KEY"
]

if __name__ == "__main__":
	check_required_env_vars(REQUIRED_ENV_VARS)
	logger.info("Starting SRAG report generation pipeline...")
	run_graph()
	logger.info("=== PIPELINE FINISHED! PDF report generated in resources/reports ===")