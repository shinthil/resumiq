# resume_parser.py

import spacy
import re
from pdfminer.high_level import extract_text
import docx

# Load Spacy Model
try:
    nlp = spacy.load("en_core_web_sm")
except:
    import os
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")


def extract_text_from_file(filepath):

    try:

        if filepath.endswith(".pdf"):
            return extract_text(filepath)

        elif filepath.endswith(".docx"):

            doc = docx.Document(filepath)

            return "\n".join(
                para.text
                for para in doc.paragraphs
            )

        else:

            with open(
                filepath,
                "r",
                encoding="utf-8"
            ) as f:

                return f.read()

    except Exception as e:

        print("Error extracting text:", e)

        return ""


def parse_resume(filepath):

    text = extract_text_from_file(filepath)

    doc = nlp(text)

    text_lower = text.lower()

    # ==========================
    # CONTACT INFO
    # ==========================

    entities = []

    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

    phone_pattern = r"\+?\d[\d -]{8,12}\d"

    emails = re.findall(
        email_pattern,
        text
    )

    phones = re.findall(
        phone_pattern,
        text
    )

    if emails:
        entities.append(
            (emails[0], "Email")
        )

    if phones:
        entities.append(
            (phones[0], "Phone")
        )

    # ==========================
    # ENTITY EXTRACTION
    # ==========================

    allowed_labels = [
        "PERSON",
        "ORG"
    ]

    seen_entities = set()

    common_skills = {
        "python",
        "java",
        "react",
        "html",
        "css",
        "javascript",
        "sql",
        "c++",
        "mern",
        "next.js"
    }

    for ent in doc.ents:

        clean_text = ent.text.strip()

        if (
            ent.label_ in allowed_labels
            and len(clean_text) > 3
            and clean_text.lower() not in common_skills
            and clean_text not in seen_entities
        ):

            entities.append(
                (
                    clean_text,
                    ent.label_
                )
            )

            seen_entities.add(
                clean_text
            )

    # ==========================
    # SKILL DATABASE
    # ==========================

    skill_db = [

        # Languages
        "Python",
        "Java",
        "C++",
        "C",
        "JavaScript",
        "SQL",

        # Frontend
        "HTML",
        "CSS",
        "React",
        "Next.js",
        "Tailwind",
        "Bootstrap",

        # Backend
        "Node.js",
        "Express",
        "Flask",
        "FastAPI",

        # Database
        "MySQL",
        "MongoDB",
        "PostgreSQL",
        "SQLite",

        # AI / ML
        "Machine Learning",
        "Deep Learning",
        "NLP",
        "TensorFlow",
        "PyTorch",
        "Scikit-learn",
        "Pandas",
        "NumPy",

        # Cloud / DevOps
        "Docker",
        "AWS",
        "Git",
        "GitHub",
        "Linux",
        "Vercel",
        "Render",

        # Other
        "REST API",
        "JWT",
        "Supabase",
        "Firebase",

        # DSA
        "Data Structures",
        "Algorithms",

        # Full Stack
        "MERN",

        # Additional
        "OpenAI",
        "LangChain",
        "LLM",
        "Generative AI",
        "Prompt Engineering",
        "Data Analysis",
        "Power BI",
        "Excel"
    ]

    # ==========================
    # SKILL EXTRACTION
    # ==========================

    found_skills = []

    for skill in skill_db:

        pattern = r"\b" + re.escape(
            skill.lower()
        ) + r"\b"

        count = len(
            re.findall(
                pattern,
                text_lower
            )
        )

        if count > 0:

            score = min(
                count * 2,
                10
            )

            found_skills.append(
                (
                    skill,
                    score
                )
            )

    found_skills.sort(
        key=lambda x: x[1],
        reverse=True
    )

    # ==========================
    # FEEDBACK GENERATION
    # ==========================

    feedback = []

    if len(found_skills) < 8:

        feedback.append(
            "Add more technical skills relevant to your target role."
        )

    if not emails:

        feedback.append(
            "Email address not detected."
        )

    if "github" not in text_lower:

        feedback.append(
            "Add GitHub profile link."
        )

    if "linkedin" not in text_lower:

        feedback.append(
            "Add LinkedIn profile link."
        )

    if "project" not in text_lower:

        feedback.append(
            "Add a dedicated Projects section."
        )

    if "internship" not in text_lower:

        feedback.append(
            "Add internship or practical experience."
        )

    if "%" not in text:

        feedback.append(
            "Quantify achievements using metrics or percentages."
        )

    action_verbs = [
        "developed",
        "implemented",
        "created",
        "built",
        "designed",
        "optimized",
        "deployed"
    ]

    if not any(
        word in text_lower
        for word in action_verbs
    ):

        feedback.append(
            "Use action verbs like Developed, Built, Designed, Implemented."
        )

    if len(feedback) == 0:

        feedback.append(
            "Excellent resume structure and ATS keyword coverage."
        )

    # ==========================
    # RETURN
    # ==========================

    return {

        "text": text,

        "entities": entities,

        "skills": found_skills,

        "feedback": feedback
    }