import sqlite3


def force_add_jobs():

    # Connect to database
    conn = sqlite3.connect("portal.db")
    c = conn.cursor()

    # Clear existing jobs
    try:
        c.execute("DELETE FROM jobs")
        print("Cleared existing jobs.")

    except sqlite3.OperationalError:

        c.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY,
                title TEXT,
                description TEXT,
                company TEXT
            )
        """)

        print("Created jobs table.")

    # Insert jobs
    jobs = [

        (
            "AI/ML Engineer",
            "Python Machine Learning NLP TensorFlow Scikit-learn Deep Learning",
            "OpenAI Labs"
        ),

        (
            "Frontend Developer",
            "React Next.js Tailwind JavaScript HTML CSS",
            "Creative Tech"
        ),

        (
            "Full Stack Developer",
            "React Node.js Express MongoDB MySQL REST API",
            "Web Solutions"
        ),

        (
            "Backend Engineer",
            "Python Flask FastAPI SQL Docker",
            "Data Corp"
        ),

        (
            "Data Scientist",
            "Pandas NumPy Machine Learning Python",
            "Analytics Hub"
        ),

        (
            "NLP Engineer",
            "NLP Python Transformers Deep Learning",
            "AI Systems"
        )

    ]

    c.executemany(
        """
        INSERT INTO jobs
        (title, description, company)
        VALUES (?, ?, ?)
        """,
        jobs
    )

    conn.commit()
    conn.close()

    print("✅ SUCCESS: 6 jobs inserted into the database!")


if __name__ == "__main__":
    force_add_jobs()