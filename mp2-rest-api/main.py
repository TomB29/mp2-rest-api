import io
import json
import logging
from pathlib import Path
import pandas as pd
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from src import DatasetInfo, DatasetStorage, HealthResponse, setup_logging

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
    #listdata = df.head(limit)
    records = json.loads(df.head(limit).to_json(orient="records"))

    return {"ID" : dataset_id, "Data" : records, "Total Length" : df.shape[0]}
    