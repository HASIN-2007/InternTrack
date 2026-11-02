import sqlite3
from flask import Flask, render_template, request, redirect

app = Flask(__name__)


def init_db():
    conn = sqlite3.connect("database.db")
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
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/add", methods=["GET", "POST"])
def add_application():
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
            conn = sqlite3.connect("database.db")
            conn.execute(
                """INSERT INTO applications
                (company_name, job_role, job_type, location, applied_date,
                 deadline, application_status, job_link, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (company_name, job_role, job_type, location, applied_date,
                 deadline, application_status, job_link, notes),
            )
            conn.commit()
            conn.close()
            return redirect("/")

    return render_template("add.html", error=error)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)