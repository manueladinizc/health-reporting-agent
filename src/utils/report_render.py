
import os
import json
import logging
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from typing import Any, Dict
from .logs import setup_logging


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
REPORTS_DIR = PROJECT_ROOT / "resources" / "reports"
JSON_DIR = PROJECT_ROOT / "resources" / "json"
TEMPLATES_DIR = PROJECT_ROOT / "src" / "template"
HTML_OUTPUT = REPORTS_DIR / "srag_report.html"

setup_logging()
logger = logging.getLogger(__name__)

def get_latest_report_json() -> str:
    """Find the most recent srag_report_*.json in the resources/json directory."""
    json_files = list(JSON_DIR.glob("srag_report_*.json"))
    if not json_files:
        raise FileNotFoundError("Nenhum arquivo de relatório JSON encontrado.")
    latest_file = max(json_files, key=os.path.getctime)
    return str(latest_file)

def load_report_data(json_path: str) -> Dict[str, Any]:
    """Load report data from a JSON file."""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def render_html_report(data: dict, template_name: str = "report.html") -> str:
    """Render the HTML report using Jinja2."""
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    template = env.get_template(template_name)
    return template.render(report=data)

def save_html_report(html_content: str, output_path: str = str(HTML_OUTPUT)):
    """Save the rendered HTML to the resources/reports directory."""
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
        logger.info(f"HTML saved at: {output_path}")
