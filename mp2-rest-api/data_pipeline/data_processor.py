import logging
import pandas as pd
import sys
logger = logging.getLogger(__name__)

def remove_duplicates(df):
    """Remove exact duplicate rows."""
    # Remove exact duplicate rows.
    df_non_dupe = df.drop_duplicates()
    # Log a DEBUG message containing the before and after row counts.
    logger.debug(f"Initial number of rows -> {df.shape[0]}\nNow cointains {df_non_dupe.shape[0]} rows")
    # Return the resulting DataFrame.
    return(df_non_dupe)

def handle_missing(df, axis="rows"):
    """Drop rows or columns containing missing values."""
    if axis=="rows":
        logger.info("Axis selected is Rows: Removing rows with missing values")
        """Remove rows containing missing values."""
        # Drop rows containing one or more missing values.
        rows_less_dropped = df.dropna()
        # Log a DEBUG message containing the before and after row counts.
        logger.debug(f"Initial number of rows -> {df.shape[0]}\nNow cointains {rows_less_dropped.shape[0]} rows")
        # Return the resulting DataFrame.
        return(rows_less_dropped)
    elif axis=="columns":
        logger.info("Axis selected is Columns: Removing columns with missing values")
        """Remove columns containing missing values."""
        columns_less_dropped = df.dropna(axis=1)
        logger.debug(f"Initial number of columns -> {df.shape[1]}\nNow cointains {rows_less_dropped.shape[1]} columns")
        # Return the resulting DataFrame.
        return(columns_less_dropped)
    else:
        raise ValueError(f""" {axis} is not an accepted axis input\nAccepted inputs are 'rows' or 'columns'
            \nIf no axis is stated, rows are assumed""")

def remove_outliers(df, columns, method, threshold):
    """Remove outliers from the specified numeric columns."""
    df_output = df.copy()
    if method != "iqr" and method != "zscore":
        logger.error(f"{method} is an unsuported method")
        sys.exit(1)
    for col in columns:
        if method == "zscore":
            mean = df[col].mean()
            std = df[col].std()
            df_score_in_bounds = df[((df_output[col]-mean)/std).abs() <= threshold]
        if method == "iqr":
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            print(IQR)
            print(Threshold)
            print(Threshold * IQR)
            lower_bound = Q1 - (threshold * IQR)
            upper_bound = Q3 + (threshold * IQR)
            # Calculate Q1, Q3, and IQR.
            # Use threshold to calculate lower and upper bounds.
            # Keep rows inside the bounds.
            df_score_in_bounds = df[(df_output[col] >= lower) & (df_output[col] <= upper)]
            rows_removed = df_output.shape[0] - df_score_in_bounds.shape[0]
            # Log a DEBUG message containing the bounds and the number of rows removed.
            logger.debug(f"""{col} Scores Clead via IQR method\nUpper Bound - {upper_bound}
            \nLower Bound - {lower_bound} \n {rows_removed}  Rows Removed in Cleaning""")
            # Return the resulting DataFrame.
        df_output = df_score_in_bounds

    return df_output
         
    

def process_data(df, config):
    """Apply the processing steps enabled in the configuration."""


    df_output = df.copy()

    if config["processing"]["remove_duplicates"]:
        df_output = remove_duplicates(df_output)
        logger.info(f"removed duplicates from dataframe")


    if config["processing"]["missing"]["enabled"]:
        axis = config["processing"]["missing"]["axis"]
        df_output = handle_missing(df_output, axis)
        logger.info(f"removed {axis} including missing values from dataframe")

    if config["processing"]["outliers"]["enabled"]:
        columns = config["processing"]["outliers"]["columns"]
        method = config["processing"]["outliers"]["method"]
        threshold = config["processing"]["outliers"]["threshold"]
        log_error = []
        for elt in columns:
            if elt not in df.columns:
                log_error.append(elt)
        if log_error:
            logger.warning(f"Column(s) not found: {log_error}")
        else:
            df_output = remove_outliers(df_output, columns, method, threshold)
            logger.info(f"removed outliers from dataframe using {method} method over {columns} -- Threshold value of {threshold}")
    return df_output


def create_cleaning_report(df_before, df_after):
    """Return a dictionary summarizing the cleaning results."""
    rows_before = df_before.shape[0]
    rows_after = df_after.shape[0]
    rows_removed = df_before.shape[0] - df_after.shape[0]
    columns_before = df_before.shape[1]
    columns_after = df_after.shape[1]
    columns_removed = df_before.shape[1] - df_after.shape[1]
    output_dictionary = {
        "rows_before" : rows_before,
        "rows_after" : rows_after,
        "rows_removed" : rows_removed,
        "columns_before" : columns_before,
        "columns_after" : columns_after,
        "columns_removed" : columns_removed
    }
    return output_dictionary