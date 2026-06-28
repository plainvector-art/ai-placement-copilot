"""
Semantic Candidate Ranking Engine.
Uses SentenceTransformers to embed JD and candidate profiles,
then ranks candidates by cosine similarity via NumPy.
"""
import numpy as np
from loguru import logger

_model = None

def _get_model():
    """Lazily load the SentenceTransformer model and reuse it (lazy singleton)."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        logger.info("Initializing SentenceTransformer model 'all-MiniLM-L6-v2'...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def build_candidate_text(profile: dict) -> str:
    """
    Constructs the concatenated profile string for semantic embedding.
    This is a pure helper with no side effects.
    """
    name = profile.get("name") or ""
    skills = ", ".join(profile.get("skills") or [])
    
    project_parts = []
    for p in (profile.get("projects") or [])[:3]:
        title = p.get("title") or ""
        desc = p.get("description") or ""
        project_parts.append(f"{title} {desc}")
    projects_str = " ".join(project_parts)
    
    summary = profile.get("summary") or ""
    raw_text = profile.get("raw_text") or ""
    raw_preview = raw_text[:800]
    
    components = [name, skills, projects_str, summary, raw_preview]
    return " ".join([c.strip() for c in components if c and c.strip()])


def rank_candidates(
    candidates: list[dict],   # list of parsed profile dicts from parse_resume()
    job_description: str,     # raw JD text
) -> list[dict]:
    """Ranks candidates by cosine similarity via FAISS using SentenceTransformers."""
    if not candidates:
        return []

    logger.info(f"Ranking {len(candidates)} candidates semantically...")

    # Build profile text strings
    candidate_texts = [build_candidate_text(c) for c in candidates]

    # Get model and encode profiles
    model = _get_model()
    candidate_embeddings = model.encode(candidate_texts, convert_to_numpy=True).astype('float32')

    # Encode query JD
    query_embedding = model.encode([job_description], convert_to_numpy=True).astype('float32')

    # L2-normalize vectors for cosine similarity
    candidate_norms = np.linalg.norm(candidate_embeddings, axis=1, keepdims=True)
    candidate_norms[candidate_norms == 0] = 1.0
    candidate_embeddings_norm = candidate_embeddings / candidate_norms

    query_norm = np.linalg.norm(query_embedding, axis=1, keepdims=True)
    query_norm[query_norm == 0] = 1.0
    query_embedding_norm = query_embedding / query_norm

    # Dot product of normalized vectors yields cosine similarity (shape: (1, N))
    scores = np.dot(query_embedding_norm, candidate_embeddings_norm.T)

    N = len(candidates)

    # Attach scores to the candidate profiles
    for i in range(N):
        raw_score = float(scores[0][i])
        # cosine similarity * 100, rounded to 1 decimal, clamped between 0 and 100
        semantic_score = round(raw_score * 100, 1)
        semantic_score = max(0.0, min(100.0, semantic_score))
        candidates[i]["semantic_score"] = semantic_score

    # Default missing scores to 0.0
    for candidate in candidates:
        if "semantic_score" not in candidate:
            candidate["semantic_score"] = 0.0

    # Sort descending by semantic score
    ranked_list = sorted(candidates, key=lambda x: x["semantic_score"], reverse=True)

    # Attach 1-based ranks
    for idx, candidate in enumerate(ranked_list):
        candidate["rank"] = idx + 1

    top_candidate = ranked_list[0]
    logger.info(f"Ranking complete. Top candidate: {top_candidate.get('name')} ({top_candidate.get('semantic_score')}%)")

    return ranked_list
