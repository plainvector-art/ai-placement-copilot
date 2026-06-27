"""
Ranking Explainability Engine.
Generates plain-English reasons for each candidate's rank
based on their score components and profile signals.
No AI API calls — pure rule-based logic for speed and reliability.
"""

def explain_rank(
    profile: dict,
    signals: dict,
    scores: dict,
    jd_parsed: dict,
    rank: int,
) -> dict:
    """
    Generates structured explainability dict (strengths, gaps, recruiter verdict).
    """
    candidate_name = profile.get("name") or "Candidate"
    final_score = scores.get("final_score", 0.0)

    # 1. Strengths
    all_strengths = []
    if scores.get("semantic_score", 0.0) >= 70:
        all_strengths.append("Strong semantic alignment with the job description")
    if signals.get("project_depth_score", 0.0) >= 60:
        all_strengths.append("Well-documented projects with clear tech stacks")
    if signals.get("skills_breadth_score", 0.0) >= 65:
        all_strengths.append("Broad technical skill coverage")
    if signals.get("quantification_score", 0.0) >= 60:
        all_strengths.append("Achievements backed by measurable metrics")
    if signals.get("certifications_score", 0.0) >= 70:
        all_strengths.append("Relevant professional certifications")
    if signals.get("github_present"):
        all_strengths.append("Active GitHub profile — verifiable code portfolio")
    strengths = all_strengths[:3]

    # 2. Gaps
    all_gaps = []
    if scores.get("semantic_score", 0.0) < 50:
        all_gaps.append("Low semantic match with JD requirements")
    if signals.get("project_count", 0) < 2:
        all_gaps.append("Limited project portfolio")
    if signals.get("quantification_score", 0.0) < 30:
        all_gaps.append("Bullet points lack quantified impact")
    if not signals.get("github_present"):
        all_gaps.append("No GitHub profile linked")
    gaps = all_gaps[:2]

    # 3. Recruiter Verdict
    if final_score >= 70.0:
        recruiter_verdict = "Strong shortlist"
    elif final_score >= 50.0:
        recruiter_verdict = "Consider"
    else:
        recruiter_verdict = "Deprioritise"

    return {
        "rank": rank,
        "candidate_name": candidate_name,
        "final_score": final_score,
        "strengths": strengths,
        "gaps": gaps,
        "recruiter_verdict": recruiter_verdict
    }
