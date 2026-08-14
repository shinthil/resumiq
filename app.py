from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
import os
import sqlite3

from resume_parser import parse_resume
from job_matcher import match_jobs

app = Flask(__name__)
app.secret_key = "supersecretkey"

app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
app.config["ALLOWED_EXTENSIONS"] = {"pdf", "docx", "txt"}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# ---------------------------------
# Helper Function
# ---------------------------------
def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in app.config["ALLOWED_EXTENSIONS"]
    )


# ---------------------------------
# Database Setup
# ---------------------------------
def init_db():
    conn = sqlite3.connect("portal.db")
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY,
            title TEXT,
            description TEXT,
            company TEXT
        )
    """)

    conn.commit()
    conn.close()


init_db()


# ---------------------------------
# Home Page
# ---------------------------------
@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":

        username = request.form["username"]

        session["username"] = username

        return redirect(
            url_for("candidate_dashboard")
        )

    return render_template("index.html")


# ---------------------------------
# Candidate Dashboard
# ---------------------------------
@app.route("/dashboard", methods=["GET", "POST"])
def candidate_dashboard():

    if "username" not in session:
        return redirect(url_for("index"))

    if request.method == "POST":

        if "resume" not in request.files:
            flash("No file uploaded")
            return redirect(request.url)

        file = request.files["resume"]

        if file.filename == "":
            flash("Please select a file")
            return redirect(request.url)

        if allowed_file(file.filename):

            filename = secure_filename(file.filename)

            filepath = os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )

            file.save(filepath)

            # --------------------------
            # Resume Parsing
            # --------------------------
            resume_data = parse_resume(filepath)

            # --------------------------
            # Fetch Jobs
            # --------------------------
            conn = sqlite3.connect("portal.db")
            c = conn.cursor()

            c.execute("SELECT * FROM jobs")

            db_jobs = c.fetchall()

            conn.close()

            job_list = [
                {
                    "id": row[0],
                    "title": row[1],
                    "desc": row[2],
                    "company": row[3]
                }
                for row in db_jobs
            ]

            # --------------------------
            # Job Matching
            # --------------------------
            matches = match_jobs(
                resume_data["text"],
                job_list
            )

            # --------------------------
            # ATS Score Calculation
            # --------------------------
            ats_score = 0

            # Skills (Max 40)
            ats_score += min(
                len(resume_data["skills"]) * 2,
                40
            )

            resume_text = resume_data["text"].lower()

            # GitHub
            if "github" in resume_text:
                ats_score += 10

            # LinkedIn
            if "linkedin" in resume_text:
                ats_score += 10

            # Projects
            if "project" in resume_text:
                ats_score += 20

            # Internship
            if "internship" in resume_text:
                ats_score += 10

            ats_score = min(ats_score, 100)

            return render_template(
                "analysis.html",
                username=session["username"],
                entities=resume_data["entities"],
                skills=resume_data["skills"],
                feedback=resume_data["feedback"],
                matches=matches,
                ats_score=ats_score
            )

        else:
            flash("Invalid file type!")
            return redirect(request.url)

    return render_template("dashboard.html")


# ---------------------------------
# Run Application
# ---------------------------------
if __name__ == "__main__":

    if not os.path.exists(app.config["UPLOAD_FOLDER"]):
        os.makedirs(app.config["UPLOAD_FOLDER"])

    app.run(
        debug=True
    )