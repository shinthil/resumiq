from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
import os
import sqlite3

from resume_parser import parse_resume
from job_matcher import match_jobs

app = Flask(__name__)
app.secret_key = 'supersecretkey'

app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx', 'txt'}


# -----------------------------
# Helpers
# -----------------------------
def allowed_file(filename):
    return (
        '.' in filename and
        filename.rsplit('.', 1)[1].lower()
        in app.config['ALLOWED_EXTENSIONS']
    )


# -----------------------------
# Database Setup
# -----------------------------
def init_db():
    conn = sqlite3.connect('portal.db')
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


# -----------------------------
# Home Page
# -----------------------------
@app.route('/', methods=['GET', 'POST'])
def index():

    if request.method == 'POST':

        username = request.form['username']
        role = request.form.get(
            'role',
            'candidate'
        )

        session['username'] = username
        session['role'] = role

        if role == 'recruiter':
            return redirect(
                url_for(
                    'recruiter_dashboard'
                )
            )

        return redirect(
            url_for(
                'candidate_dashboard'
            )
        )

    return render_template('index.html')


# -----------------------------
# Candidate Dashboard
# -----------------------------
@app.route('/dashboard', methods=['GET', 'POST'])
def candidate_dashboard():

    if 'username' not in session:
        return redirect(url_for('index'))

    if request.method == 'POST':

        if 'resume' not in request.files:

            flash('No file part')

            return redirect(
                request.url
            )

        file = request.files['resume']

        if not file or file.filename == '':

            flash('No selected file')

            return redirect(
                request.url
            )

        if allowed_file(file.filename):

            filename = secure_filename(
                file.filename
            )

            filepath = os.path.join(
                app.config['UPLOAD_FOLDER'],
                filename
            )

            file.save(filepath)

            # ------------------
            # Parse Resume
            # ------------------
            resume_data = parse_resume(
                filepath
            )

            # ------------------
            # Fetch Jobs
            # ------------------
            conn = sqlite3.connect(
                'portal.db'
            )

            c = conn.cursor()

            c.execute(
                "SELECT * FROM jobs"
            )

            db_jobs = c.fetchall()

            conn.close()

            job_list = [
                {
                    'id': j[0],
                    'title': j[1],
                    'desc': j[2],
                    'company': j[3]
                }
                for j in db_jobs
            ]

            # ------------------
            # Match Jobs
            # ------------------
            matches = match_jobs(
                resume_data['text'],
                job_list
            )

            # ------------------
            # ATS Score
            # ------------------
            ats_score = 0

            ats_score += min(
                len(
                    resume_data['skills']
                ) * 2,
                40
            )

            resume_text = (
                resume_data['text']
                .lower()
            )

            if "github" in resume_text:
                ats_score += 10

            if "linkedin" in resume_text:
                ats_score += 10

            if "project" in resume_text:
                ats_score += 20

            if "internship" in resume_text:
                ats_score += 10

            ats_score = min(
                ats_score,
                100
            )

            return render_template(
                'analysis.html',

                username=session['username'],

                entities=resume_data['entities'],

                skills=resume_data['skills'],

                feedback=resume_data['feedback'],

                matches=matches,

                ats_score=ats_score
            )

        else:

            flash(
                'Invalid file type!'
            )

            return redirect(
                request.url
            )

    return render_template(
        'dashboard.html'
    )


# -----------------------------
# Recruiter Dashboard
# -----------------------------
@app.route(
    '/recruiter',
    methods=['GET', 'POST']
)
def recruiter_dashboard():

    if request.method == 'POST':

        title = request.form['title']
        company = request.form['company']
        desc = request.form['description']

        conn = sqlite3.connect(
            'portal.db'
        )

        c = conn.cursor()

        c.execute(
            """
            INSERT INTO jobs
            (title, description, company)
            VALUES (?, ?, ?)
            """,
            (
                title,
                desc,
                company
            )
        )

        conn.commit()

        conn.close()

        flash(
            'Job Posted Successfully!'
        )

        return redirect(
            url_for(
                'recruiter_dashboard'
            )
        )

    conn = sqlite3.connect(
        'portal.db'
    )

    c = conn.cursor()

    c.execute(
        """
        SELECT title,
               description,
               company
        FROM jobs
        """
    )

    jobs = c.fetchall()

    conn.close()

    return render_template(
        'recruiter.html',
        jobs=jobs
    )


# -----------------------------
# Run App
# -----------------------------
if __name__ == '__main__':

    if not os.path.exists(
        app.config['UPLOAD_FOLDER']
    ):
        os.makedirs(
            app.config['UPLOAD_FOLDER']
        )

    app.run(
        debug=True
    )