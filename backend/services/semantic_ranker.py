"""
Semantic Candidate Ranking Engine.
Uses API-based embeddings (Gemini/OpenAI) or local TF-IDF fallback
to compute cosine similarity and rank candidate resumes.
"""
import numpy as np
from loguru import logger

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


def _local_tfidf_similarity(candidate_texts: list[str], query_text: str) -> np.ndarray:
    """
    Computes cosine similarity using a simple local TF-IDF model in pure Python/NumPy.
    Returns a numpy array of shape (1, len(candidate_texts)) containing scores between 0 and 1.
    """
    import re
    # Tokenize function
    def tokenize(text: str) -> list[str]:
        words = re.findall(r'\b[a-zA-Z0-9_]{2,}\b', text.lower())
        return words

    # Stopwords (minimal set to avoid bloating)
    stopwords = {
        'and', 'the', 'for', 'with', 'in', 'on', 'at', 'to', 'of', 'a', 'an', 'is', 'are', 'was', 'were',
        'this', 'that', 'these', 'those', 'it', 'its', 'we', 'our', 'you', 'your', 'they', 'their', 'he', 'she'
    }

    # Tokenize candidates and query
    cand_tokens = [[w for w in tokenize(t) if w not in stopwords] for t in candidate_texts]
    query_tokens = [w for w in tokenize(query_text) if w not in stopwords]

    # Build vocabulary of unique terms
    vocab = sorted(list(set(query_tokens + [w for tokens in cand_tokens for w in tokens])))
    if not vocab:
        return np.zeros((1, len(candidate_texts)))

    word_to_idx = {w: i for i, w in enumerate(vocab)}
    V = len(vocab)
    N = len(candidate_texts)

    # Document frequency
    df = np.zeros(V)
    for tokens in cand_tokens:
        unique_tokens = set(tokens)
        for t in unique_tokens:
            if t in word_to_idx:
                df[word_to_idx[t]] += 1
    # Add query to df
    for t in set(query_tokens):
        if t in word_to_idx:
            df[word_to_idx[t]] += 1

    # IDF
    idf = np.log((N + 2) / (df + 1)) + 1.0

    # Vectorize function
    def get_tfidf_vector(tokens: list[str]) -> np.ndarray:
        vec = np.zeros(V)
        for t in tokens:
            if t in word_to_idx:
                vec[word_to_idx[t]] += 1
        # Apply TF-IDF formula (sublinear TF scaling)
        tf = np.where(vec > 0, 1.0 + np.log(vec), 0.0)
        return tf * idf

    # Create embedding matrices
    candidate_embeddings = np.array([get_tfidf_vector(tokens) for tokens in cand_tokens]) # (N, V)
    query_embedding = get_tfidf_vector(query_tokens).reshape(1, -1) # (1, V)

    # Calculate norms
    cand_norms = np.linalg.norm(candidate_embeddings, axis=1, keepdims=True)
    cand_norms[cand_norms == 0] = 1.0
    cand_emb_norm = candidate_embeddings / cand_norms

    query_norm = np.linalg.norm(query_embedding, axis=1, keepdims=True)
    query_norm[query_norm == 0] = 1.0
    query_emb_norm = query_embedding / query_norm

    # Dot product: shape (1, N)
    scores = np.dot(query_emb_norm, cand_emb_norm.T)
    return scores


def rank_candidates(
    candidates: list[dict],   # list of parsed profile dicts from parse_resume()
    job_description: str,     # raw JD text
) -> list[dict]:
    """Ranks candidates by cosine similarity using API-based embeddings or a local TF-IDF fallback."""
    if not candidates:
        return []

    logger.info(f"Ranking {len(candidates)} candidates semantically...")

    # Build profile text strings
    candidate_texts = [build_candidate_text(c) for c in candidates]

    # Try API-based embeddings first if AI is configured
    from backend.services.ai_client import is_ai_configured, embed_text
    
    use_api = is_ai_configured()
    scores = None

    if use_api:
        try:
            logger.info("Attempting to generate embeddings via API...")
            # Generate candidate embeddings
            candidate_embeddings = np.array(embed_text(candidate_texts), dtype=np.float32)
            # Generate query embedding
            query_embedding = np.array(embed_text([job_description]), dtype=np.float32)
            
            # L2-normalize vectors for cosine similarity
            candidate_norms = np.linalg.norm(candidate_embeddings, axis=1, keepdims=True)
            candidate_norms[candidate_norms == 0] = 1.0
            candidate_embeddings_norm = candidate_embeddings / candidate_norms

            query_norm = np.linalg.norm(query_embedding, axis=1, keepdims=True)
            query_norm[query_norm == 0] = 1.0
            query_embedding_norm = query_embedding / query_norm

            # Dot product of normalized vectors yields cosine similarity (shape: (1, N))
            scores = np.dot(query_embedding_norm, candidate_embeddings_norm.T)
            logger.info("API embeddings and cosine similarity calculated successfully.")
        except Exception as e:
            logger.warning(f"API embedding generation failed: {e}. Falling back to local TF-IDF...")
            use_api = False

    if not use_api or scores is None:
        logger.info("Using local TF-IDF vectorizer fallback...")
        scores = _local_tfidf_similarity(candidate_texts, job_description)

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
