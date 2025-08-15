import os
import sys
import logging
from typing import List

logger = logging.getLogger(__name__)

def check_required_env_vars(required_vars: List[str]):
    """
    Checks if all required environment variables are set. If any are missing, logs an error and exits.
    """
    missing = [var for var in required_vars if not os.getenv(var)]
    if missing:
        logger.error(f"Missing required environment variables: {', '.join(missing)}")
        sys.exit(1)
