import io


def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert "db_exists" in data


def test_history_initially_empty(client):
    response = client.get("/api/history")
    assert response.status_code == 200
    assert response.get_json() == []


def test_screen_endpoint_accepts_txt_resume(client):
    resume_stream = io.BytesIO(b"Python SQL developer with experience")
    data = {
        "job_title": "Software Engineer",
        "job_description": "Looking for Python and SQL experience",
        "resumes": (resume_stream, "resume.txt"),
    }
    response = client.post("/api/screen", data=data, content_type="multipart/form-data")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["job_title"] == "Software Engineer"
    assert payload["results"]
    assert payload["results"][0]["filename"] == "resume.txt"
    assert "matched_skills" in payload["results"][0]


def test_screen_requires_job_description(client):
    resume_stream = io.BytesIO(b"Python developer")
    data = {
        "job_title": "Developer",
        "job_description": "",
        "resumes": (resume_stream, "resume.txt"),
    }
    response = client.post("/api/screen", data=data, content_type="multipart/form-data")
    assert response.status_code == 400
