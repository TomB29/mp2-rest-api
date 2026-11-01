import logging
from pathlib import Path
logger = logging.getLogger(__name__)

def validate_input(filepath):
    """Check whether the input path exists and is a file."""
    if not Path(filepath).is_file():
        logger.error(f"Could not locate file requested in argument: {filepath.name}")
        raise FileNotFoundError(f"Input file not found: {filepath.name}")
    else:
        logger.info(f"Input file validated: {Path(filepath)}")
        return True

def setup_logging(verbose=False):
    """Configure logging for the pipeline."""
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
        datefmt='%H:%M:%S'
        )

