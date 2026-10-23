import os
import re
import secrets
import sqlite3
from pathlib import Path

import bcrypt
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_wtf.csrf import CSRFProtect

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "users.db"

app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get("SECRET_KEY") or secrets.token_hex(32),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE", "0") == "1",
    PERMANENT_SESSION_LIFETIME=1800,
    MAX_CONTENT_LENGTH=16 * 1024,
)
csrf = CSRFProtect(app)


def get_db():
    connection = sqlite3.connect(DATABASE, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_db() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE COLLATE NOCASE,
                password BLOB NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )


def validate_username(username):
    return bool(re.fullmatch(r"[A-Za-z0-9_.-]{3,30}", username))


def validate_password(password):
    # bcrypt considers at most 72 bytes; reject oversized values instead of silently truncating.
    encoded = password.encode("utf-8")
    return 8 <= len(encoded) <= 72


@app.after_request
def add_security_headers(response):
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault(
        "Content-Security-Policy",
        "default-src 'self' https://cdn.jsdelivr.net; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
        "script-src 'self' 'unsafe-inline'; img-src 'self' data:; "
        "form-action 'self'; frame-ancestors 'none'; base-uri 'self'",
    )
    return response


@app.route("/")
def home():
    if session.get("user_id"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not validate_username(username):
            flash("Username must be 3–30 characters using letters, numbers, ., _, or -.", "danger")
            return render_template("register.html"), 400

        if not validate_password(password):
            flash("Password must be at least 8 characters and no more than 72 UTF-8 bytes.", "danger")
            return render_template("register.html"), 400

        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12))
        try:
            with get_db() as connection:
                connection.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, password_hash),
                )
        except sqlite3.IntegrityError:
            flash("That username is already registered. Please choose another.", "warning")
            return render_template("register.html"), 409
        except sqlite3.Error:
            app.logger.exception("Database error during registration")
            flash("We could not create your account right now. Please try again.", "danger")
            return render_template("register.html"), 500

        flash("Account created successfully. You can now log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        try:
            with get_db() as connection:
                user = connection.execute(
                    "SELECT id, username, password FROM users WHERE username = ? COLLATE NOCASE",
                    (username,),
                ).fetchone()
        except sqlite3.Error:
            app.logger.exception("Database error during login")
            flash("Login is temporarily unavailable. Please try again.", "danger")
            return render_template("login.html"), 500

        password_ok = False
        if user and validate_password(password):
            try:
                password_ok = bcrypt.checkpw(password.encode("utf-8"), user["password"])
            except (ValueError, TypeError):
                password_ok = False

        if not password_ok:
            flash("Invalid username or password.", "danger")
            return render_template("login.html"), 401

        session.clear()
        session.permanent = True
        session["user_id"] = user["id"]
        session["user"] = user["username"]
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if not session.get("user_id"):
        flash("Please log in to view your dashboard.", "warning")
        return redirect(url_for("login"))
    return render_template("dashboard.html", user=session.get("user", "User"))


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("login"))


@app.errorhandler(413)
def request_too_large(_error):
    return "Request too large.", 413


init_db()

if __name__ == "__main__":
    # Debug mode is deliberately off by default.
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")), debug=False)
