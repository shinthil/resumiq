from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


SKILLS = [
    "python","java","c++","sql","react","next.js",
    "javascript","html","css","node.js","express",
    "mongodb","mysql","tailwind","git","github",
    "machine learning","deep learning","nlp",
    "tensorflow","pytorch","flask","fastapi",
    "docker","aws","mern"
]


def extract_skills(text):

    text = text.lower()

    found = set()

    for skill in SKILLS:
        if skill in text:
            found.add(skill)

    return found


def match_jobs(resume_text, job_list):

    if not job_list:
        return []

    resume_skills = extract_skills(resume_text)

    descriptions = [job["desc"] for job in job_list]
    corpus = [resume_text] + descriptions

    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(corpus)

    cosine_scores = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:]
    )[0]

    matches = []

    for i, job in enumerate(job_list):

        job_skills = extract_skills(job["desc"])

        if len(job_skills) > 0:

            skill_score = (
                len(resume_skills & job_skills)
                / len(job_skills)
            )

        else:
            skill_score = 0

        tfidf_score = cosine_scores[i]

        final_score = (
            0.4 * tfidf_score +
            0.6 * skill_score
        ) * 100

        matches.append({
            "title": job["title"],
            "score": round(final_score),

            "matched_skills":
                list(resume_skills & job_skills),

            "missing_skills":
                list(job_skills - resume_skills)
        })

    matches.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return matches