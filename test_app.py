import sqlite3

import pytest

from app import create_app


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "test.db"


@pytest.fixture
def app(db_path):
    app = create_app(db_path)
    app.config["TESTING"] = True
    app.config["ADMIN_PASSWORD"] = "test-password"
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def rows(db_path):
    with sqlite3.connect(db_path) as db:
        return db.execute("SELECT name, email, major FROM signups").fetchall()


def test_module_exposes_app_for_gunicorn():
    import app as app_module
    assert app_module.app.name == "app"


def test_form_page_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b'name="email"' in response.data


def test_signup_saves_and_redirects(client, db_path):
    response = client.post(
        "/",
        data={"name": "Ada", "email": "ada@example.edu", "major": "Math"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Thank you" in response.data
    assert rows(db_path) == [("Ada", "ada@example.edu", "Math")]


def test_missing_field_is_rejected(client, db_path):
    response = client.post("/", data={"name": "Ada", "email": "", "major": "Math"})
    assert response.status_code == 400
    assert rows(db_path) == []


def sign_up(client, name, email, major):
    client.post("/", data={"name": name, "email": email, "major": major})


def test_admin_requires_password(client):
    response = client.get("/admin")
    assert response.status_code == 401
    assert "WWW-Authenticate" in response.headers


def test_admin_rejects_wrong_password(client):
    response = client.get("/admin", auth=("admin", "wrong"))
    assert response.status_code == 401


def test_admin_rejects_non_ascii_password(client):
    response = client.get("/admin", auth=("admin", "café"))
    assert response.status_code == 401


def test_admin_locked_when_password_not_configured(app, client):
    app.config["ADMIN_PASSWORD"] = None
    response = client.get("/admin", auth=("admin", ""))
    assert response.status_code == 401


def test_admin_lists_every_signup(client):
    sign_up(client, "Ada", "ada@example.edu", "Math")
    sign_up(client, "Grace", "grace@example.edu", "Computer Science")
    response = client.get("/admin", auth=("admin", "test-password"))
    assert response.status_code == 200
    for text in (b"Ada", b"ada@example.edu", b"Math",
                 b"Grace", b"grace@example.edu", b"Computer Science"):
        assert text in response.data


def test_admin_escapes_submitted_html(client):
    sign_up(client, "<script>x</script>", "x@example.edu", "Art")
    response = client.get("/admin", auth=("admin", "test-password"))
    assert b"<script>" not in response.data
    assert b"&lt;script&gt;" in response.data


@pytest.mark.parametrize("path, auth", [
    ("/", None),
    ("/thanks", None),
    ("/admin", ("admin", "test-password")),
])
def test_pages_are_responsive(client, path, auth):
    html = client.get(path, auth=auth).data
    assert b'name="viewport" content="width=device-width, initial-scale=1"' in html
    assert b"bootstrap@5.3.3/dist/css/bootstrap.min.css" in html
