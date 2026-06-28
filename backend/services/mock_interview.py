"""
AI Mock Interview Simulator.
Chat-based interview with AI evaluation and performance scoring.
"""
import json
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from loguru import logger

from backend.services.ai_client import generate_text, generate_json
from backend.services.prompts import PROMPTS

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
    """
    name = profile.get("name", "Candidate")
    skills = ", ".join(profile.get("skills", [])[:5])

    prompt = PROMPTS["mock_interview_start"].format(
        interviewer_persona=INTERVIEWER_PERSONA,
        name=name,
        target_role=target_role,
        skills=skills
    )

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
    conversation_text = _format_conversation(messages[-8:])

    # Determine what type of question to ask next
    question_type = _determine_next_question_type(question_count)

    prompt = PROMPTS["mock_interview_process"].format(
        interviewer_persona=INTERVIEWER_PERSONA,
        name=profile.get('name', 'Candidate'),
        target_role=target_role,
        skills=', '.join(profile.get('skills', [])[:6]),
        projects=', '.join([p.get('title', '') for p in profile.get('projects', [])[:2]]),
        question_count=question_count,
        conversation_text=conversation_text,
        question_type=question_type
    )

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
    """
    logger.info("Evaluating mock interview performance...")

    conversation_text = _format_conversation(session.get("messages", []))
    target_role = session.get("target_role", "Software Engineer")
    total_questions = session.get("question_count", 0)

    prompt = PROMPTS["mock_interview_evaluate"].format(
        evaluation_system=EVALUATION_SYSTEM,
        target_role=target_role,
        skills=', '.join(profile.get('skills', [])[:8]),
        total_questions=total_questions,
        conversation_text=conversation_text
    )

    schema = {
        "overall_score": int,
        "scores": dict,
        "strengths": list,
        "areas_for_improvement": list,
        "standout_moments": list,
        "overall_feedback": str,
        "hiring_recommendation": str,
        "next_steps": list
    }

    result = generate_json(prompt, temperature=0.3, max_tokens=2000, schema=schema)

    if not result or not isinstance(result, dict) or "overall_score" not in result:
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
    prompt = PROMPTS["mock_interview_closing"].format(
        interviewer_persona=INTERVIEWER_PERSONA,
        target_role=target_role
    )

    return generate_text(prompt, temperature=0.7, max_tokens=200)


def _calculate_duration(session: Dict) -> str:
    """Calculate approximate interview duration."""
    messages = session.get("messages", [])
    if len(messages) >= 2:
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
