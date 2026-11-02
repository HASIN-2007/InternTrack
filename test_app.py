import sqlite3
import pytest
import app as app_module


def register_user(client, email="test@example.com", password="secret123",
                  name="Test User"):
    return client.post("/register", data={
        "full_name": name,
        "email": email,
        "password": password,
        "confirm_password": password,
    })


def login_user(client, email="test@example.com", password="secret123"):
    return client.post("/login", data={
        "email": email,
        "password": password,
    })


@pytest.fixture
def anon_client(tmp_path):
    app_module.DATABASE = str(tmp_path / "test.db")
    app_module.init_db()
    app_module.app.config["TESTING"] = True
    return app_module.app.test_client()


@pytest.fixture
def client(anon_client):
    register_user(anon_client)
    login_user(anon_client)
    return anon_client


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


# ----- Application features (logged in) -----

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


# ----- Login and security -----

def test_dashboard_requires_login(anon_client):
    response = anon_client.get("/")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_other_pages_require_login(anon_client):
    for url in ["/add", "/export", "/edit/1"]:
        response = anon_client.get(url)
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]


def test_register_and_login(anon_client):
    register_user(anon_client)
    response = login_user(anon_client)
    assert response.status_code == 302

    home = anon_client.get("/")
    assert home.status_code == 200
    assert b"Test User" in home.data


def test_register_duplicate_email(anon_client):
    register_user(anon_client)
    response = register_user(anon_client)
    assert b"An account with this email already exists." in response.data


def test_register_short_password(anon_client):
    response = register_user(anon_client, password="abc")
    assert b"Password must be at least 6 characters." in response.data


def test_login_wrong_password(anon_client):
    register_user(anon_client)
    response = login_user(anon_client, password="wrongpass")
    assert b"Invalid email or password." in response.data


def test_logout(client):
    client.post("/logout")
    response = client.get("/")
    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


def test_password_is_hashed(anon_client):
    register_user(anon_client, password="secret123")
    conn = sqlite3.connect(app_module.DATABASE)
    saved = conn.execute("SELECT password_hash FROM users").fetchone()[0]
    conn.close()
    assert saved != "secret123"
    assert "secret123" not in saved


def test_users_see_only_their_own_applications(client):
    add_sample(client, company="Google")

    other = app_module.app.test_client()
    register_user(other, email="other@example.com", name="Other User")
    login_user(other, email="other@example.com")

    assert b"Google" not in other.get("/").data
    assert other.get("/edit/1").status_code == 404

    other.post("/delete/1")
    assert b"Google" in client.get("/").data