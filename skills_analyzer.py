from sklearn.feature_extraction.text import CountVectorizer

def extract_skills(text):
    skill_vocab = ["python", "java", "machine learning", "sql", "communication", "c++", "react", "docker"]
    vectorizer = CountVectorizer(vocabulary=skill_vocab)
    X = vectorizer.fit_transform([text.lower()])
    skills_counts = dict(zip(skill_vocab, X.toarray()[0]))
    ranked = sorted(skills_counts.items(), key=lambda x: x[1], reverse=True)
    return ranked
