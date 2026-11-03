import io
import json
import logging
from pathlib import Path
import pandas as pd
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from src import (DatasetInfo, DatasetStorage, HealthResponse, setup_logging, OutlierSettings, 
ValidationSettings, MissingSettings, ProcessingSettings, ProcessConfig, ProcessingReport, log_requests)
from data_pipeline import create_cleaning_report, process_data, validate_dataframe

setup_logging(verbose=True)
logger = logging.getLogger(__name__)

app = FastAPI(title="Data Processing API", version="1.0.0")
storage = DatasetStorage()

@app.get("/health", response_model=HealthResponse)
def health_check():
    """Return the application status and version."""
    return {"status": "ok", "version": "1.0.0"}

@app.post("/upload", response_model=DatasetInfo)
async def upload_dataset(file: UploadFile = File(...)):
    """Read and store a CSV upload."""
    if Path(file.filename).suffix != ".csv":
        logger.warning(f"Uploaded File {file} is not supported CSV type")
        raise HTTPException( status_code=400, detail="Unsuported File Type")
    content = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(content))
    except (pd.errors.EmptyDataError,pd.errors.ParserError,UnicodeDecodeError) as error:
        logger.error(f"Unexpected Error Occured - {error}")
        raise HTTPException(status_code=400, detail=f"Unexpected {error} Occured")
    
    dataset_id = storage.save(df, file.filename)

    logger.info(f"{file.filename} saved under dataset id {dataset_id}, containing {df.shape[0]} rows")

    return DatasetInfo(
            id=dataset_id,
            filename=file.filename,
            rows=df.shape[0],
            columns=df.shape[1],
            column_names=df.columns.tolist()
    )


@app.get("/datasets/{dataset_id}")
def get_dataset(dataset_id: int, limit: int = Query(default=100, ge=1)):
    """Return up to limit rows from a stored dataset."""
    df = storage.get(dataset_id)
    if df is None:
        logger.warning(f"ID not found: {dataset_id}")
        raise HTTPException(status_code=404, detail=f"ID {dataset_id} not found")
    records = json.loads(df.head(limit).to_json(orient="records"))

    return {"ID" : dataset_id, "Data" : records, "Total Length" : df.shape[0]}


@app.post( "/datasets/{dataset_id}/process", response_model=ProcessingReport)
def process_dataset(dataset_id: int, config: ProcessConfig):
    """Validate and process a stored dataset using MP1 functions."""

    df = storage.get(dataset_id)
    if df is None:
        logger.warning(f"ID not found: {dataset_id}")
        raise HTTPException(status_code=404, detail=f"ID {dataset_id} not found")
    config_dict = config.model_dump()
    required_columns = config_dict["validation"]["required_columns"]
    numeric_columns = config_dict["validation"]["numeric_columns"]

    exists = df.columns

    for elt in numeric_columns:
        if elt not in exists:
            raise HTTPException(status_code=400, detail=f"required column {elt} not found")
            logger.error(f"{elt} does not exist in dataframe")
    logger.info(f"All Required Columns Exist\n{numeric_columns}")

    try:
        df_val = (validate_dataframe(df, required_columns, numeric_columns)).copy()
        val_lines_removed = df.shape[0] - df_val.shape[0]
        logger.info(f"{val_lines_removed} rows removed in validation [containg null values]")

        df_proc = process_data(df_val, config_dict)
        clr_report = create_cleaning_report(df_val, df_proc)

    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))


    storage.update(dataset_id, df_proc)
    logger.info(f"{dataset_id} updated using validation and cleaning configuration")

    return ProcessingReport(
        id=dataset_id,
        validation_rows_removed=val_lines_removed,
        cleaning_report=clr_report
    )
