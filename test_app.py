import base64

import pytest

from app import app, get_db


@pytest.fixture
def client(tmp_path):
    db_path = tmp_path / "test.db"
    app.config.update(TESTING=True, DATABASE=str(db_path))
    with app.test_client() as client:
        yield client, db_path


def rows(db_path):
    assert app.config["DATABASE"] == str(db_path)
    conn = get_db()
    try:
        return conn.execute("SELECT name, email, major FROM signups").fetchall()
    finally:
        conn.close()


def test_form_renders(client):
    c, _ = client
    resp = c.get("/")
    assert resp.status_code == 200
    assert b"<form" in resp.data
    assert b"bootstrap" in resp.data


def test_valid_signup_saves_and_redirects(client):
    c, db_path = client
    resp = c.post(
        "/",
        data={"name": "Ada", "email": "ada@example.edu", "major": "Math"},
        follow_redirects=True,
    )
    assert resp.status_code == 200
    assert b"Thank you" in resp.data
    assert rows(db_path) == [("Ada", "ada@example.edu", "Math")]


def test_missing_field_is_rejected(client):
    c, db_path = client
    resp = c.post("/", data={"name": "Ada", "email": "ada@example.edu", "major": ""})
    assert resp.status_code == 400
    assert b"Please fill in every field" in resp.data
    assert rows(db_path) == []


ADMIN_PW = "test-admin-pw"


def basic_auth(password, username="admin"):
    token = base64.b64encode(f"{username}:{password}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


@pytest.fixture
def admin_client(client, monkeypatch):
    monkeypatch.setenv("ADMIN_PASSWORD", ADMIN_PW)
    return client


def add_signup(c, name, email, major):
    resp = c.post("/", data={"name": name, "email": email, "major": major})
    assert resp.status_code == 302


def test_admin_requires_password(admin_client):
    c, _ = admin_client
    resp = c.get("/admin")
    assert resp.status_code == 401
    assert resp.headers["WWW-Authenticate"].startswith("Basic")


def test_admin_rejects_wrong_password(admin_client):
    c, _ = admin_client
    add_signup(c, "Ada", "ada@example.edu", "Math")
    resp = c.get("/admin", headers=basic_auth("wrong"))
    assert resp.status_code == 401
    assert b"ada@example.edu" not in resp.data


def test_admin_locked_when_password_not_configured(client, monkeypatch):
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)
    c, _ = client
    assert c.get("/admin", headers=basic_auth("")).status_code == 401
    assert c.get("/admin", headers=basic_auth("None")).status_code == 401


def test_admin_lists_every_signup(admin_client):
    c, _ = admin_client
    add_signup(c, "Ada", "ada@example.edu", "Math")
    add_signup(c, "Grace", "grace@example.edu", "Computer Science")
    resp = c.get("/admin", headers=basic_auth(ADMIN_PW))
    assert resp.status_code == 200
    for value in (b"Ada", b"ada@example.edu", b"Math",
                  b"Grace", b"grace@example.edu", b"Computer Science"):
        assert value in resp.data
    assert b"2 signups" in resp.data


def test_admin_shows_empty_state(admin_client):
    c, _ = admin_client
    resp = c.get("/admin", headers=basic_auth(ADMIN_PW))
    assert resp.status_code == 200
    assert b"No signups yet" in resp.data


def test_admin_escapes_signup_data(admin_client):
    c, _ = admin_client
    add_signup(c, "<script>alert(1)</script>", "x@example.edu", "Math")
    resp = c.get("/admin", headers=basic_auth(ADMIN_PW))
    assert b"<script>alert(1)</script>" not in resp.data
    assert b"&lt;script&gt;" in resp.data


def test_invalid_email_is_rejected(client):
    c, db_path = client
    resp = c.post("/", data={"name": "Ada", "email": "not-an-email", "major": "Math"})
    assert resp.status_code == 400
    assert rows(db_path) == []
