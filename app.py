import csv
import io
import os
import sqlite3
from flask import (Flask, render_template, request, redirect, abort,
                   Response, session)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY",
    "dev-secret-key-change-me"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE = os.environ.get(
    "DATABASE_PATH",
    os.path.join(BASE_DIR, "database.db")
)


def init_db():
    conn = sqlite3.connect(DATABASE)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            job_role TEXT NOT NULL,
            job_type TEXT,
            location TEXT,
            applied_date TEXT,
            deadline TEXT,
            application_status TEXT NOT NULL DEFAULT 'Applied',
            job_link TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER
        )
    """)

    columns = [row[1] for row in conn.execute("PRAGMA table_info(applications)")]
    if "user_id" not in columns:
        conn.execute("ALTER TABLE applications ADD COLUMN user_id INTEGER")

    conn.commit()
    conn.close()


@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect("/")

    error = None

    if request.method == "POST":
        full_name = request.form["full_name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        if full_name == "" or email == "" or password == "":
            error = "All fields are required."
        elif "@" not in email:
            error = "Enter a valid email address."
        elif len(password) < 6:
            error = "Password must be at least 6 characters."
        elif password != confirm_password:
            error = "Passwords do not match."
        else:
            conn = sqlite3.connect(DATABASE)
            existing = conn.execute(
                "SELECT id FROM users WHERE email = ?", (email,)
            ).fetchone()

            if existing is not None:
                error = "An account with this email already exists."
                conn.close()
            else:
                conn.execute(
                    "INSERT INTO users (full_name, email, password_hash) "
                    "VALUES (?, ?, ?)",
                    (full_name, email, generate_password_hash(password)),
                )
                conn.commit()
                conn.close()
                return redirect("/login")

    return render_template("register.html", error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect("/")

    error = None

    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
        conn.close()

        if user is None or not check_password_hash(user["password_hash"], password):
            error = "Invalid email or password."
        else:
            session.clear()
            session["user_id"] = user["id"]
            session["user_name"] = user["full_name"]
            return redirect("/")

    return render_template("login.html", error=error)


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect("/login")


@app.route("/")
def home():
    if "user_id" not in session:
        return redirect("/login")
    user_id = session["user_id"]

    search = request.args.get("search", "").strip()
    status = request.args.get("status", "")

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row

    query = "SELECT * FROM applications WHERE user_id = ?"
    params = [user_id]

    if search != "":
        query += " AND (company_name LIKE ? OR job_role LIKE ?)"
        params.append("%" + search + "%")
        params.append("%" + search + "%")

    if status != "":
        query += " AND application_status = ?"
        params.append(status)

    query += " ORDER BY id DESC"
    applications = conn.execute(query, params).fetchall()

    total = conn.execute(
        "SELECT COUNT(*) FROM applications WHERE user_id = ?",
        (user_id,),
    ).fetchone()[0]
    applied = conn.execute(
        "SELECT COUNT(*) FROM applications "
        "WHERE user_id = ? AND application_status = ?",
        (user_id, "Applied"),
    ).fetchone()[0]
    interview = conn.execute(
        "SELECT COUNT(*) FROM applications "
        "WHERE user_id = ? AND application_status = ?",
        (user_id, "Interview"),
    ).fetchone()[0]
    selected = conn.execute(
        "SELECT COUNT(*) FROM applications "
        "WHERE user_id = ? AND application_status = ?",
        (user_id, "Selected"),
    ).fetchone()[0]

    conn.close()
    return render_template(
        "index.html",
        applications=applications,
        total=total,
        applied=applied,
        interview=interview,
        selected=selected,
        search=search,
        status=status,
    )


@app.route("/add", methods=["GET", "POST"])
def add_application():
    if "user_id" not in session:
        return redirect("/login")
    user_id = session["user_id"]

    error = None

    if request.method == "POST":
        company_name = request.form["company_name"].strip()
        job_role = request.form["job_role"].strip()
        job_type = request.form["job_type"]
        location = request.form["location"].strip()
        applied_date = request.form["applied_date"]
        deadline = request.form["deadline"]
        application_status = request.form["application_status"]
        job_link = request.form["job_link"].strip()
        notes = request.form["notes"].strip()

        if company_name == "" or job_role == "":
            error = "Company name and job role are required."
        else:
            conn = sqlite3.connect(DATABASE)
            conn.execute(
                """INSERT INTO applications
                (user_id, company_name, job_role, job_type, location,
                 applied_date, deadline, application_status, job_link, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (user_id, company_name, job_role, job_type, location,
                 applied_date, deadline, application_status, job_link, notes),
            )
            conn.commit()
            conn.close()
            return redirect("/")

    return render_template("add.html", error=error)


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_application(id):
    if "user_id" not in session:
        return redirect("/login")
    user_id = session["user_id"]

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    application = conn.execute(
        "SELECT * FROM applications WHERE id = ? AND user_id = ?",
        (id, user_id),
    ).fetchone()

    if application is None:
        conn.close()
        abort(404)

    error = None

    if request.method == "POST":
        company_name = request.form["company_name"].strip()
        job_role = request.form["job_role"].strip()
        job_type = request.form["job_type"]
        location = request.form["location"].strip()
        applied_date = request.form["applied_date"]
        deadline = request.form["deadline"]
        application_status = request.form["application_status"]
        job_link = request.form["job_link"].strip()
        notes = request.form["notes"].strip()

        if company_name == "" or job_role == "":
            error = "Company name and job role are required."
            application = {
                "id": id,
                "company_name": company_name,
                "job_role": job_role,
                "job_type": job_type,
                "location": location,
                "applied_date": applied_date,
                "deadline": deadline,
                "application_status": application_status,
                "job_link": job_link,
                "notes": notes,
            }
        else:
            conn.execute(
                """UPDATE applications
                SET company_name = ?, job_role = ?, job_type = ?,
                    location = ?, applied_date = ?, deadline = ?,
                    application_status = ?, job_link = ?, notes = ?
                WHERE id = ? AND user_id = ?""",
                (company_name, job_role, job_type, location, applied_date,
                 deadline, application_status, job_link, notes, id, user_id),
            )
            conn.commit()
            conn.close()
            return redirect("/")

    conn.close()
    return render_template("edit.html", application=application, error=error)


@app.route("/delete/<int:id>", methods=["POST"])
def delete_application(id):
    if "user_id" not in session:
        return redirect("/login")
    user_id = session["user_id"]

    conn = sqlite3.connect(DATABASE)
    conn.execute(
        "DELETE FROM applications WHERE id = ? AND user_id = ?",
        (id, user_id),
    )
    conn.commit()
    conn.close()
    return redirect("/")


@app.route("/export")
def export_csv():
    if "user_id" not in session:
        return redirect("/login")
    user_id = session["user_id"]

    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT * FROM applications WHERE user_id = ? ORDER BY id DESC",
        (user_id,),
    ).fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Company", "Role", "Job Type", "Location", "Applied Date",
        "Deadline", "Status", "Job Link", "Notes",
    ])
    for row in rows:
        writer.writerow([
            row["company_name"], row["job_role"], row["job_type"],
            row["location"], row["applied_date"], row["deadline"],
            row["application_status"], row["job_link"], row["notes"],
        ])

    response = Response(output.getvalue(), mimetype="text/csv")
    response.headers["Content-Disposition"] = (
        "attachment; filename=applications.csv"
    )
    return response


# Initialize database when the application starts
init_db()

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")