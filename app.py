import hmac
import os
import sqlite3

from flask import Flask, Response, redirect, render_template, request, url_for


def create_app(database="signups.db"):
    app = Flask(__name__)
    app.config["DATABASE"] = database
    app.config["ADMIN_PASSWORD"] = os.environ.get("ADMIN_PASSWORD")

    def get_db():
        return sqlite3.connect(app.config["DATABASE"])

    with get_db() as db:
        db.execute(
            "CREATE TABLE IF NOT EXISTS signups ("
            "id INTEGER PRIMARY KEY, name TEXT NOT NULL, "
            "email TEXT NOT NULL, major TEXT NOT NULL)"
        )

    @app.route("/", methods=["GET", "POST"])
    def signup():
        if request.method == "POST":
            fields = [request.form.get(k, "").strip() for k in ("name", "email", "major")]
            if all(fields):
                with get_db() as db:
                    db.execute(
                        "INSERT INTO signups (name, email, major) VALUES (?, ?, ?)",
                        fields,
                    )
                return redirect(url_for("thanks"))
            return render_template("signup.html", error="All fields are required."), 400
        return render_template("signup.html")

    @app.route("/thanks")
    def thanks():
        return render_template("thanks.html")

    @app.route("/admin")
    def admin():
        expected = app.config["ADMIN_PASSWORD"]
        given = request.authorization.password if request.authorization else None
        # Stay locked if no password is configured.
        if not expected or not given or not hmac.compare_digest(
            given.encode(), expected.encode()
        ):
            return Response(
                "Password required.", 401,
                {"WWW-Authenticate": 'Basic realm="admin"'},
            )
        with get_db() as db:
            signups = db.execute(
                "SELECT name, email, major FROM signups ORDER BY id"
            ).fetchall()
        return render_template("admin.html", signups=signups)

    return app

app = create_app()
