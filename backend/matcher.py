def match_resume(text):

    jobs = {
        "Software Developer": ["python", "java", "c++", "git", "flask"],
        "Data Analyst": ["python", "excel", "sql", "pandas", "data"],
        "Web Developer": ["html", "css", "javascript", "react"]
    }

    text = text.lower()

    best_score = 0
    best_role = ""
    best_matched = []
    best_missing = []

    for role, skills in jobs.items():

        matched = []
        missing = []

        for skill in skills:
            if skill in text:
                matched.append(skill)
            else:
                missing.append(skill)

        score = int((len(matched) / len(skills)) * 100)

        if score > best_score:
            best_score = score
            best_role = role
            best_matched = matched
            best_missing = missing

    return {
        "best_role": best_role,
        "score": best_score,
        "matched_skills": best_matched,
        "missing_skills": best_missing
    }