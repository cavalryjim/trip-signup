import hmac
import os
import sqlite3

from flask import Flask, Response, redirect, render_template, request, url_for

app = Flask(__name__)
app.config["DATABASE"] = "signups.db"

FIELDS = ("name", "email", "major")


def get_db():
    conn = sqlite3.connect(app.config["DATABASE"])
    conn.execute(
        "CREATE TABLE IF NOT EXISTS signups ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT, "
        "name TEXT NOT NULL, email TEXT NOT NULL, major TEXT NOT NULL, "
        "created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"
    )
    return conn


@app.route("/", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        form = {f: request.form.get(f, "").strip() for f in FIELDS}
        if all(form.values()) and "@" in form["email"]:
            with get_db() as conn:
                conn.execute(
                    "INSERT INTO signups (name, email, major) VALUES (?, ?, ?)",
                    (form["name"], form["email"], form["major"]),
                )
            conn.close()
            return redirect(url_for("thanks"))
        return render_template(
            "signup.html", form=form, error="Please fill in every field with a valid email."
        ), 400
    return render_template("signup.html", form={}, error=None)


@app.route("/thanks")
def thanks():
    return render_template("thanks.html")


def admin_authorized():
    expected = os.environ.get("ADMIN_PASSWORD")
    print(f"The expected password is {expected}")
    auth = request.authorization
    if not expected or auth is None or auth.password is None:
        return False
    return hmac.compare_digest(auth.password.encode(), expected.encode())


@app.route("/admin")
def admin():
    if not admin_authorized():
        return Response(
            "Password required.", 401, {"WWW-Authenticate": 'Basic realm="Admin"'}
        )
    conn = get_db()
    try:
        signups = conn.execute(
            "SELECT name, email, major, created_at FROM signups ORDER BY id"
        ).fetchall()
    finally:
        conn.close()
    return render_template("admin.html", signups=signups)
