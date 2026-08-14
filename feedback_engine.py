# feedback_engine.py

def generate_feedback(
        skills,
        entities,
        resume_text):

    feedback = []

    skill_names = [
        s[0].lower()
        for s in skills
    ]

    if len(skills) < 5:
        feedback.append(
            "Add more technical skills."
        )

    if "github" not in resume_text.lower():
        feedback.append(
            "Add GitHub profile link."
        )

    if "linkedin" not in resume_text.lower():
        feedback.append(
            "Add LinkedIn profile link."
        )

    if "project" not in resume_text.lower():
        feedback.append(
            "Add project section."
        )

    if "internship" not in resume_text.lower():
        feedback.append(
            "Add internships or practical experience."
        )

    if "%" not in resume_text:
        feedback.append(
            "Quantify achievements using numbers."
        )

    if len(feedback) == 0:
        feedback.append(
            "Excellent resume structure."
        )

    return feedback