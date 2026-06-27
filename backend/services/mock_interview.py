"""
AI Mock Interview Simulator.
Chat-based interview with AI evaluation and performance scoring.
"""
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from loguru import logger

from backend.services.ai_client import generate_text, generate_json


INTERVIEWER_PERSONA = """You are Alex, a senior technical interviewer at a top tech company. 
You conduct professional, encouraging, yet rigorous interviews. You:
- Ask one focused question at a time
- Listen carefully and ask relevant follow-up questions
- Are encouraging but evaluate rigorously
- Keep responses concise (2-4 sentences max)
- Score mentally: communication, technical depth, problem-solving, confidence"""

EVALUATION_SYSTEM = """You are an expert interview evaluator. Analyze the interview conversation 
and provide detailed, constructive, actionable feedback."""


def start_interview(
    profile: Dict,
    target_role: str,
    interview_type: str = "comprehensive",
) -> Dict:
    """
    Initialize a new mock interview session.

    Returns:
        Initial greeting message and session config
    """
    name = profile.get("name", "there")
    skills = ", ".join(profile.get("skills", [])[:5])

    prompt = f"""{INTERVIEWER_PERSONA}

You are starting a mock interview with {name}, who is applying for {target_role}.
Their key skills include: {skills}

Write a warm, professional opening greeting (2-3 sentences) that:
1. Introduces yourself as Alex
2. Sets the stage for the interview
3. Asks your first HR/warm-up question

Keep it natural and conversational."""

    greeting = generate_text(prompt, temperature=0.8, max_tokens=300)

    return {
        "session_id": f"mock_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "target_role": target_role,
        "interviewer": "Alex",
        "messages": [
            {"role": "assistant", "content": greeting, "timestamp": datetime.now().isoformat()}
        ],
        "question_count": 0,
        "max_questions": 15,
        "status": "active",
    }


def process_response(
    session: Dict,
    user_response: str,
    profile: Dict,
) -> Dict:
    """
    Process user's interview response and generate AI follow-up.

    Args:
        session: Current interview session dict
        user_response: Candidate's response text
        profile: Candidate profile

    Returns:
        Updated session with AI response
    """
    messages = session.get("messages", [])
    question_count = session.get("question_count", 0)
    target_role = session.get("target_role", "Software Engineer")

    # Add user message
    messages.append({
        "role": "user",
        "content": user_response,
        "timestamp": datetime.now().isoformat(),
    })

    question_count += 1

    # Check if interview should end
    if question_count >= session.get("max_questions", 15):
        closing = _generate_closing(messages, target_role)
        messages.append({
            "role": "assistant",
            "content": closing,
            "timestamp": datetime.now().isoformat(),
            "is_closing": True,
        })
        session["messages"] = messages
        session["question_count"] = question_count
        session["status"] = "completed"
        return session

    # Build conversation history for context
    conversation_text = _format_conversation(messages[-8:])  # Last 8 messages

    # Determine what type of question to ask next
    question_type = _determine_next_question_type(question_count)

    prompt = f"""{INTERVIEWER_PERSONA}

Interview Context:
- Candidate: {profile.get('name', 'Candidate')}
- Target Role: {target_role}
- Key Skills: {', '.join(profile.get('skills', [])[:6])}
- Projects: {', '.join([p.get('title', '') for p in profile.get('projects', [])[:2]])}
- Question Number: {question_count} of 15

Recent Conversation:
{conversation_text}

The candidate just responded. Now:
1. Briefly acknowledge their response (1 sentence, natural and encouraging)
2. Ask a {question_type} question

IMPORTANT: 
- If their answer was weak/incomplete, ask a follow-up to probe deeper
- If their answer was strong, pivot to a new challenge area
- Keep your total response to 3-4 sentences maximum
- Be natural and conversational"""

    ai_response = generate_text(prompt, temperature=0.75, max_tokens=400)

    messages.append({
        "role": "assistant",
        "content": ai_response,
        "timestamp": datetime.now().isoformat(),
        "question_num": question_count,
        "question_type": question_type,
    })

    session["messages"] = messages
    session["question_count"] = question_count

    return session


def evaluate_interview(session: Dict, profile: Dict) -> Dict:
    """
    Evaluate completed interview and generate performance report.

    Args:
        session: Completed interview session
        profile: Candidate profile

    Returns:
        Detailed performance evaluation report
    """
    logger.info("Evaluating mock interview performance...")

    conversation_text = _format_conversation(session.get("messages", []))
    target_role = session.get("target_role", "Software Engineer")
    total_questions = session.get("question_count", 0)

    prompt = f"""{EVALUATION_SYSTEM}

Interview Details:
- Target Role: {target_role}
- Candidate Skills: {', '.join(profile.get('skills', [])[:8])}
- Total Questions: {total_questions}

Full Interview Transcript:
{conversation_text}

Evaluate the candidate comprehensively. Return JSON:
{{
  "overall_score": <0-100>,
  "scores": {{
    "communication": {{"score": <0-100>, "feedback": "..."}},
    "technical_knowledge": {{"score": <0-100>, "feedback": "..."}},
    "problem_solving": {{"score": <0-100>, "feedback": "..."}},
    "confidence": {{"score": <0-100>, "feedback": "..."}},
    "cultural_fit": {{"score": <0-100>, "feedback": "..."}}
  }},
  "strengths": ["...", "...", "..."],
  "areas_for_improvement": ["...", "...", "..."],
  "standout_moments": ["..."],
  "overall_feedback": "2-3 sentence executive summary",
  "hiring_recommendation": "Strong Yes / Yes / Maybe / No",
  "next_steps": ["...", "...", "..."]
}}"""

    result = generate_json(prompt, temperature=0.3, max_tokens=2000)

    if not result:
        result = _fallback_evaluation(session)

    result["session_duration"] = _calculate_duration(session)
    result["questions_answered"] = total_questions

    return result


def _format_conversation(messages: List[Dict]) -> str:
    """Format messages into readable conversation text."""
    lines = []
    for msg in messages:
        role = "Interviewer (Alex)" if msg["role"] == "assistant" else "Candidate"
        lines.append(f"{role}: {msg['content']}")
    return "\n\n".join(lines)


def _determine_next_question_type(question_num: int) -> str:
    """Determine what type of question to ask based on interview progression."""
    if question_num <= 2:
        return "warm-up HR"
    elif question_num <= 6:
        return "technical knowledge"
    elif question_num <= 10:
        return "deep-dive project or problem-solving"
    elif question_num <= 13:
        return "behavioral (STAR format)"
    else:
        return "closing (aspirations/questions for us)"


def _generate_closing(messages: List[Dict], target_role: str) -> str:
    """Generate a professional interview closing."""
    prompt = f"""{INTERVIEWER_PERSONA}

This mock interview for a {target_role} position is now complete (15 questions answered).
Write a warm, professional closing statement (3-4 sentences) that:
1. Thanks the candidate for their time
2. Notes one genuinely positive aspect you observed
3. Tells them to click 'View Report' for detailed feedback"""

    return generate_text(prompt, temperature=0.7, max_tokens=200)


def _calculate_duration(session: Dict) -> str:
    """Calculate approximate interview duration."""
    messages = session.get("messages", [])
    if len(messages) >= 2:
        # Estimate ~2 min per question
        questions = session.get("question_count", 5)
        return f"~{questions * 2} minutes"
    return "~10 minutes"


def _fallback_evaluation(session: Dict) -> Dict:
    """Fallback evaluation when AI is unavailable."""
    return {
        "overall_score": 65,
        "scores": {
            "communication": {"score": 65, "feedback": "Generally clear communication"},
            "technical_knowledge": {"score": 60, "feedback": "Demonstrated foundational knowledge"},
            "problem_solving": {"score": 65, "feedback": "Showed structured thinking"},
            "confidence": {"score": 70, "feedback": "Spoke with reasonable confidence"},
            "cultural_fit": {"score": 65, "feedback": "Positive attitude throughout"},
        },
        "strengths": ["Engaged throughout the interview", "Provided relevant examples"],
        "areas_for_improvement": ["Add more quantified examples", "Practice STAR format answers"],
        "overall_feedback": "Solid performance with room for growth. Focus on quantifying achievements and deepening technical knowledge.",
        "hiring_recommendation": "Maybe",
        "next_steps": ["Practice 2-3 mock interviews weekly", "Study system design concepts", "Prepare 5 STAR-format stories"],
    }
