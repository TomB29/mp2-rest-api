# data_loaders.py
from pathlib import Path
import logging
import pandas as pd
import json
import yaml
#mp1-part2.md 2026-09-23
#3 / 6
# Do not call logging.basicConfig() here.
# Use the logging configuration from Part 1.
logger = logging.getLogger(__name__)
def load_csv(filepath):
    """Load a CSV file into a DataFrame.
    filepath is a Path object.
    """
    dataframeobj = pd.read_csv(filepath)
    rows = len(dataframeobj.index)
    logger.info(f"Loaded CSV file: {Path(filepath).name} ({rows} row(s))")
    return dataframeobj


def load_json(filepath):
    """Load a JSON file into a Python object (dict or list).
    filepath is a Path object.
    """
    with open(filepath, "r") as file:
        data = json.load(file)
    logger.info(f"Loaded JSON file: {Path(filepath).name}")
    return data
    
def load_yaml(filepath):
    """Load a YAML file into a Python object.
    filepath is a Path object.
    """
    with open(filepath, "r") as f:
        config_yamlobj = yaml.safe_load(f)
    logger.info(f"Yaml File Loaded: {Path(filepath).name}")
    return config_yamlobj

def load_data(filepath):
    """Load a file based on its extension.
    filepath is a string, such as 'fixtures/sample.csv'
    """
    # split filepath at . -> return csv, json, yaml
    if Path(filepath).suffix == ".csv":
        return load_csv(filepath)
    elif Path(filepath).suffix == ".json":
        return load_json(filepath)
    elif Path(filepath).suffix == ".yaml":
        return load_yaml(filepath)
    else:
        print (Path(filepath).suffix)
        logger.error(f"{Path(filepath).name} is not in a supported file type")
        raise ValueError(f"Unsuported file type - {Path(filepath).name}")