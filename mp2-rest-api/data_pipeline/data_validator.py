# src/data_validator.py
import logging
import pandas as pd
logger = logging.getLogger(__name__)
def validate_dataframe(df, required_columns, numeric_columns):
    """Validate the DataFrame and return valid data.
    required_columns: a list of column names that must exist.
    numeric_columns: a list of column names whose values should be
    numeric.
    """
    df_copy = df.copy()
    log_error = []
    for elt in required_columns:
        if elt not in df.columns.to_list():
            print(df.columns.to_list())
            log_error.append(elt)
        if log_error:
            logger.error(f"Column(s) not found: {log_error}")
            ValueError(f"Required Columns not found in dataframe - {log_error}")
    for col in numeric_columns:
        invalid_rows = []
        for i, value in df[col].items():
            if pd.notna(value):
                try:
                    float(value)
                except ValueError:
                    # TODO: Log a warning and record this row's index.
                    logger.warning(f"Column {col} row index {i} contains a non-numerable value")
                    invalid_rows.append(i)
    df = df.drop(invalid_rows)
    df[col] = pd.to_numeric(df[col])
    logger.debug(f"Dataframe contains {df.shape[0]} valid rows, {(df_copy.shape[0] - df.shape[0])} rows removed")
    return df

