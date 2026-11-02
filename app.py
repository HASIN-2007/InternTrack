import sqlite3
from flask import Flask, render_template, request, redirect, abort

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
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    applications = conn.execute(
        "SELECT * FROM applications ORDER BY id DESC"
    ).fetchall()

    total = conn.execute(
        "SELECT COUNT(*) FROM applications"
    ).fetchone()[0]
    applied = conn.execute(
        "SELECT COUNT(*) FROM applications WHERE application_status = ?",
        ("Applied",),
    ).fetchone()[0]
    interview = conn.execute(
        "SELECT COUNT(*) FROM applications WHERE application_status = ?",
        ("Interview",),
    ).fetchone()[0]
    selected = conn.execute(
        "SELECT COUNT(*) FROM applications WHERE application_status = ?",
        ("Selected",),
    ).fetchone()[0]

    conn.close()
    return render_template(
        "index.html",
        applications=applications,
        total=total,
        applied=applied,
        interview=interview,
        selected=selected,
    )


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


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_application(id):
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    application = conn.execute(
        "SELECT * FROM applications WHERE id = ?", (id,)
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
                WHERE id = ?""",
                (company_name, job_role, job_type, location, applied_date,
                 deadline, application_status, job_link, notes, id),
            )
            conn.commit()
            conn.close()
            return redirect("/")

    conn.close()
    return render_template("edit.html", application=application, error=error)


@app.route("/delete/<int:id>", methods=["POST"])
def delete_application(id):
    conn = sqlite3.connect("database.db")
    conn.execute("DELETE FROM applications WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)