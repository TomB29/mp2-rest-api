import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def save_data(df, filepath):
    """Save a DataFrame as a CSV file."""
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(filepath, index=False)
    logger.debug(f"{df.shape[0]} rows saved to {Path(filepath)}")
    return filepath
