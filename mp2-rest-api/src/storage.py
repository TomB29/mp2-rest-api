import logging

logger = logging.getLogger(__name__)


class DatasetStorage:
    def __init__(self):
        self._store = {}
        self._counter = 0

    def save(self, df, filename):
        "Saves Copy of Dataset into dataset"
        self._counter =+ 1
        dataset_id = self._counter
        self._store[dataset_id] = {"filename" : filename, "data" : df.copy()}
        logger.debug(f"Stored dataset: id={dataset_id}, rows={len(df)}")
        return dataset_id

    def get(self, dataset_id):
        """Return a copy of the stored DataFrame, or None."""
        element = self._store.get(dataset_id)
        if element is None:
            logger.debug(f"Dataset not found -- ID {dataset_id}")
            return None
        logger.debug(f"Retrieved Dataset -- ID {dataset_id} == {element.shape[0]} rows")
        return element["data"].copy()

    def get_metadata(self, dataset_id):
        """Return the dataset metadata, or None."""
        element = self._store.get(dataset_id)
        if element is None:
            logger.debug(f"Dataset not found -- ID {dataset_id}")
            return None
        df = element["data"].copy()
        logger.debug(f"Retrieved Dataset Metadata -- ID {dataset_id}")
        return {"Dataset ID" : dataset_id, "Filename" : element["filename"], "Rows" : df.shape[0],
            "Columns" : df.shape[1], "Column Names" : df.columns.tolist()}

    def update(self, dataset_id, df):
        """Replace an existing dataset; return True, or False if missing."""
        element = self._store.get(dataset_id)
        if element is None:
            logger.debug(f"Dataset not found -- ID {dataset_id}")
            return False
        logger.debug(f"Updating Dataset -- ID {dataset_id}")
        element['data'] = df
        return True

    def clear(self):
        """Clear all data and reset the ID counter."""
        self._store.clear()
        self._counter = 0