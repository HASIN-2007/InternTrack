import pytest
import app as app_module


@pytest.fixture
def client(tmp_path):
    app_module.DATABASE = str(tmp_path / "test.db")
    app_module.init_db()
    app_module.app.config["TESTING"] = True
    return app_module.app.test_client()


def add_sample(client, company="Google", role="SDE Intern", status="Applied"):
    return client.post("/add", data={
        "company_name": company,
        "job_role": role,
        "job_type": "Internship",
        "location": "Bengaluru",
        "applied_date": "2026-10-20",
        "deadline": "2026-11-15",
        "application_status": status,
        "job_link": "",
        "notes": "",
    })


def test_home_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Dashboard" in response.data


def test_add_application(client):
    add_sample(client)
    response = client.get("/")
    assert b"Google" in response.data
    assert b"SDE Intern" in response.data


def test_add_requires_company_and_role(client):
    response = add_sample(client, company="", role="SDE Intern")
    assert b"Company name and job role are required." in response.data

    home = client.get("/")
    assert b"SDE Intern" not in home.data


def test_edit_application(client):
    add_sample(client, status="Applied")
    client.post("/edit/1", data={
        "company_name": "Google",
        "job_role": "SDE Intern",
        "job_type": "Internship",
        "location": "Bengaluru",
        "applied_date": "2026-10-20",
        "deadline": "2026-11-15",
        "application_status": "Interview",
        "job_link": "",
        "notes": "",
    })
    response = client.get("/")
    assert b"badge-interview" in response.data
    assert b"badge-applied" not in response.data


def test_edit_missing_application_returns_404(client):
    response = client.get("/edit/999")
    assert response.status_code == 404


def test_delete_application(client):
    add_sample(client)
    client.post("/delete/1")
    response = client.get("/")
    assert b"Google" not in response.data


def test_search_by_company(client):
    add_sample(client, company="Google")
    add_sample(client, company="Amazon")
    response = client.get("/?search=amazon")
    assert b"Amazon" in response.data
    assert b"Google" not in response.data


def test_filter_by_status(client):
    add_sample(client, company="Google", status="Applied")
    add_sample(client, company="Amazon", status="Interview")
    response = client.get("/?status=Interview")
    assert b"Amazon" in response.data
    assert b"Google" not in response.data


def test_dashboard_counts(client):
    add_sample(client, company="Google", status="Applied")
    add_sample(client, company="Amazon", status="Applied")
    add_sample(client, company="Microsoft", status="Interview")
    response = client.get("/")
    assert b"<h2>3</h2>" in response.data
    assert b"<h2>2</h2>" in response.data
    assert b"<h2>1</h2>" in response.data


def test_export_csv(client):
    add_sample(client)
    response = client.get("/export")
    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    assert "attachment" in response.headers["Content-Disposition"]
    assert b"Company,Role" in response.data
    assert b"Google" in response.data