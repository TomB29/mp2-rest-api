#TESTS

def test_upload_csv(client, sample_csv_bytes):
    responsejson = client.post("/upload", 
        files={"file": ("sample_data.csv", sample_csv_bytes, "text/csv")})
    assert responsejson.status_code == 200

    responseclean = responsejson.json()
    assert responseclean["rows"] == 6
    assert responseclean["columns"] == 2
    assert responseclean["id"] > 0



def test_process_and_retrieve(client, uploaded_dataset_id, processing_body):
    responsejson = client.post(
        f"/datasets/{uploaded_dataset_id}/process", json=processing_body)
    assert responsejson.status_code == 200

    response_dict = responsejson.json()
    assert response_dict["validation_rows_removed"] == 1
    assert response_dict["cleaning_report"]["rows_before"] == 5
    assert response_dict["cleaning_report"]["rows_after"] == 3
    # TODO 2: GET /datasets/{uploaded_dataset_id}.
    # Assert status 200 and total_rows == 3.
    # Check that the returned records contain student IDs
    # 1, 2, and 5 with scores 80, 90, and 85.
    gather = client.get(f"/datasets/{uploaded_dataset_id}")
    assert gather.status_code == 200

    gather_dict = gather.json()
    assert gather_dict["Total Length"] == 3
    df = gather_dict["Data"]
    assert [rows["student_id"] for rows in df] == [1, 2, 5]
    assert [rows["score"] for rows in df] == [80, 90, 85]



def test_retrieve_missing_dataset(client):
    call = client.post("/emptylocation/123123")
    assert call.status_code == 404
    