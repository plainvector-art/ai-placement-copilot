"""
Prompts module for versioned, centralized AI prompt templates.
Includes templates for JD parsing, candidate insights, coaching, interviews, roadmaps, and match analyses.
"""

# Version 1.0.0
PROMPTS = {
    "recruiter_insights": """You are an expert technical recruiter. Analyze the candidate's profile against the job description requirements.
    
    JOB TITLE: {role_title}
    REQUIRED SKILLS: {required_skills}
    DOMAIN: {domain}
    
    CANDIDATE PROFILE:
    - Name: {name}
    - Skills: {skills}
    - Summary: {summary}
    - Semantic Fit Score: {semantic_score}%
    - ATS Quality Score: {ats_score}%
    
    Generate a JSON object with the following keys:
    - "fit_analysis": "A detailed 2-3 sentence recruiter assessment of how well this candidate fits the role."
    - "technical_vetting_points": ["2-3 specific technical topics or skills on their resume that match the job and should be verified"]
    - "suggested_interview_questions": ["2 custom interview questions to ask this candidate based on their background and gaps"]
    
    Make sure the response contains ONLY valid JSON and no code block wrappers.""",

    "jd_parser": """Analyze the following job description and extract the structured requirements:
    
    JOB DESCRIPTION:
    {jd_text}
    
    Extract the information as a JSON object with these exact keys:
    - "role_title": string — inferred job title
    - "seniority_level": string — one of: Intern, Junior, Mid, Senior, Lead
    - "required_skills": list of must-have technical skills
    - "preferred_skills": list of nice-to-have skills
    - "key_responsibilities": list of top 4 responsibilities as short phrases
    - "minimum_experience_years": integer representing years of experience, or null if not specified
    - "domain": string — e.g. Data Analytics, Backend Engineering, ML/AI, Front-End, DevOps, Full-Stack, etc.
    - "red_flags_for_mismatch": list of 2-3 things that would disqualify a candidate immediately
    
    Make sure the response contains ONLY valid JSON and no code block wrappers.""",

    "career_coach_chat": """{system_persona}

=== CANDIDATE CONTEXT ===
{context}

=== CONVERSATION HISTORY ===
{history_text}
=== NEW MESSAGE ===
Student: {user_message}

Respond as CareerCopilot Coach. Be specific, reference their actual profile data, and give actionable steps they can take TODAY.""",

    "cover_letter": """Write a compelling, professional cover letter for {name} applying for {target_role}{company_clause}.

CANDIDATE PROFILE:
- Skills: {skills}
- Key Projects: {projects}
- Experience entries: {experience_count}
- Email: {email}

{jd_context}

Requirements:
- Opening paragraph: Hook + why this role excites them
- Middle paragraphs: Specific achievements + how skills match the role (reference 2-3 real skills)
- Closing: Call to action, confidence, next steps
- Professional but personable tone
- 300-400 words total
- Do NOT use generic phrases like "I am writing to express my interest"
- Reference specific technologies and projects naturally
- Make it sound HUMAN, not AI-generated

Format as a proper business letter.""",

    "linkedin_headline": """Generate LinkedIn profile content for {name} targeting {target_role}.

Current Skills: {skills}
Certifications: {certs}

Return JSON:
{{
  "headlines": [
    "Option 1: keyword-rich, role-specific headline",
    "Option 2: achievement-focused headline",
    "Option 3: aspirational headline with current state"
  ],
  "about_section": "3-4 paragraph LinkedIn About section. Professional, personable, includes key skills and what makes them unique. End with a call to connect.",
  "skills_to_add": ["...", "...", "..."],
  "connection_message_template": "Short personalized connection request message template"
}}""",

    "career_path": """Map out a realistic 5-year career path for someone targeting {target_role}.

Current profile:
- Skills: {skills}
- Projects: {projects_count}
- Experience: {experience_count} entries

Return JSON:
{{
  "current_level": "...",
  "path": [
    {{"year": 0, "role": "...", "salary_range": "...", "key_skills": ["..."], "companies": ["types"]}},
    {{"year": 1, "role": "...", "salary_range": "...", "key_skills": ["..."], "milestone": "..."}},
    {{"year": 2, "role": "...", "salary_range": "...", "key_skills": ["..."], "milestone": "..."}},
    {{"year": 3, "role": "...", "salary_range": "...", "key_skills": ["..."], "milestone": "..."}},
    {{"year": 5, "role": "...", "salary_range": "...", "key_skills": ["..."], "milestone": "..."}}
  ],
  "alternative_paths": ["...", "..."],
  "salary_trajectory": "...",
  "advice": "..."
}}""",

    "salary_estimate": """Estimate realistic salary ranges for a {target_role} candidate in {location}.

Profile strength:
- Skills count: {skills_count} ({skills_list})
- Experience entries: {experience_count}
- Certifications: {cert_count}

Return JSON:
{{
  "entry_level": {{"min": <number>, "max": <number>, "typical": <number>}},
  "mid_level": {{"min": <number>, "max": <number>, "typical": <number>}},
  "senior_level": {{"min": <number>, "max": <number>, "typical": <number>}},
  "candidate_estimate": {{"min": <number>, "max": <number>, "level": "Entry/Mid/Senior"}},
  "top_paying_companies": ["...", "...", "..."],
  "skills_that_increase_salary": ["...", "...", "..."],
  "negotiation_tips": ["...", "..."],
  "currency": "USD"
}}""",

    "interview_questions": """Generate a comprehensive interview question set for a {target_role} candidate.

CANDIDATE PROFILE:
- Name: {name}
- Key Skills: {skills_str}
- Projects: {project_summary}
- Certifications: {certs}
- Difficulty Level: {difficulty}

Generate exactly this structure in JSON:
{{
  "hr_questions": [
    {{"id": 1, "question": "...", "category": "HR", "difficulty": "Easy", "tip": "..."}}
  ],
  "technical_questions": [
    {{"id": 1, "question": "...", "category": "Technical", "difficulty": "Medium/Hard", "tip": "...", "expected_topics": ["..."]}}
  ],
  "project_questions": [
    {{"id": 1, "question": "...", "category": "Project", "difficulty": "Medium", "tip": "..."}}
  ],
  "behavioral_questions": [
    {{"id": 1, "question": "...", "category": "Behavioral", "difficulty": "Medium", "tip": "...", "framework": "STAR"}}
  ]
}}

Make questions highly specific to the candidate's background. Reference actual skills and projects.
Technical questions should test real knowledge needed for {target_role}.""",

    "learning_roadmap": """{roadmap_system}

Create a comprehensive personalized learning roadmap for {name} targeting the {target_role} role.

CURRENT STATE:
- Existing Skills: {existing_skills}
- Missing Required Skills: {missing_skills}
- Priority Skills to Learn: {priority_skills}
- Available Study Time: {available_hours} hours/week

Create a practical, actionable roadmap in this exact JSON structure:
{{
  "summary": {{
    "target_role": "{target_role}",
    "total_duration": "6 months",
    "total_hours": <number>,
    "key_focus_areas": ["...", "...", "..."],
    "expected_outcome": "..."
  }},
  "phases": {{
    "phase_1": {{
      "name": "Foundation Building",
      "duration": "30 days",
      "weeks": 4,
      "goal": "...",
      "weeks_breakdown": [
        {{
          "week": 1,
          "focus": "...",
          "topics": ["...", "..."],
          "project": "...",
          "hours": <number>,
          "resources": [
            {{"title": "...", "type": "Course/Book/Video/Practice", "url": "...", "free": true/false}}
          ],
          "milestone": "..."
        }}
      ],
      "phase_project": "...",
      "skills_gained": ["...", "..."],
      "milestone": "..."
    }},
    "phase_2": {{
      "name": "Core Skills Development",
      "duration": "60 days",
      "weeks": 8,
      "goal": "..."
    }},
    "phase_3": {{
      "name": "Advanced Skills & Projects",
      "duration": "90 days",
      "weeks": 12,
      "goal": "..."
    }},
    "phase_4": {{
      "name": "Interview Prep & Job Search",
      "duration": "6 months",
      "weeks": 24,
      "goal": "..."
    }}
  }}
}}

Be highly specific to their real missing skills. Provide real, valuable learning resources. Ensure projects are practical and build portfolio credibility.""",

    "jd_match": """Analyze the fit between a {name}'s resume and this job description.

CANDIDATE SKILLS: {skills}
CANDIDATE PROJECTS: {projects}
BASE MATCH SCORE: {base_score}%

JOB DESCRIPTION (first 800 chars):
{jd_snippet}

Provide JSON:
{{
  "fit_assessment": "2-sentence assessment of overall fit",
  "strong_fit_reasons": ["...", "..."],
  "concern_areas": ["...", "..."],
  "interview_talking_points": ["...", "...", "..."],
  "resume_tailoring_tips": ["...", "..."]
}}""",

    "project_recs": """Recommend 5 specific, unique portfolio projects for a {level} {target_role} candidate.

Their existing skills: {skills}
Projects they already have: {existing_projects}

Return JSON:
{{
  "projects": [
    {{
      "title": "...",
      "description": "2-3 sentence project description",
      "why_build": "Why this project impresses {target_role} recruiters",
      "technologies": ["tech1", "tech2", "tech3"],
      "difficulty": "Beginner/Intermediate/Advanced",
      "estimated_time": "X weeks",
      "impact_score": <1-10>,
      "github_topics": ["tag1", "tag2"],
      "deployment": "Where/how to deploy",
      "what_to_add": "One unique feature that makes it stand out",
      "recruiters_love": "Why this specifically impresses recruiters"
    }}
  ],
  "build_order": ["Project 1 title", "Project 2 title"],
  "portfolio_strategy": "2-sentence strategy for maximizing portfolio impact",
  "github_tips": ["Tip 1", "Tip 2", "Tip 3"]
}}

Make projects unique, market-relevant, and different from what they already have.
Focus on projects that solve real problems and demonstrate {target_role} competencies.""",

    "mock_interview_start": """{interviewer_persona}

You are starting a mock interview with {name}, who is applying for {target_role}.
Their key skills include: {skills}

Write a warm, professional opening greeting (2-3 sentences) that:
1. Introduces yourself as Alex
2. Sets the stage for the interview
3. Asks your first HR/warm-up question

Keep it natural and conversational.""",

    "mock_interview_process": """{interviewer_persona}

Interview Context:
- Candidate: {name}
- Target Role: {target_role}
- Key Skills: {skills}
- Projects: {projects}
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
- Be natural and conversational""",

    "mock_interview_evaluate": """{evaluation_system}

Interview Details:
- Target Role: {target_role}
- Candidate Skills: {skills}
- Total Questions: {total_questions}

Full Interview Transcript:
{conversation_text}

Evaluate the candidate comprehensively. Return JSON:
{{
  "overall_score": <number>,
  "scores": {{
    "communication": {{"score": <number>, "feedback": "..."}},
    "technical_knowledge": {{"score": <number>, "feedback": "..."}},
    "problem_solving": {{"score": <number>, "feedback": "..."}},
    "confidence": {{"score": <number>, "feedback": "..."}},
    "cultural_fit": {{"score": <number>, "feedback": "..."}}
  }},
  "strengths": ["...", "...", "..."],
  "areas_for_improvement": ["...", "...", "..."],
  "standout_moments": ["..."],
  "overall_feedback": "2-3 sentence executive summary",
  "hiring_recommendation": "Strong Yes / Yes / Maybe / No",
  "next_steps": ["...", "...", "..."]
}}""",

    "mock_interview_closing": """{interviewer_persona}

This mock interview for a {target_role} position is now complete (15 questions answered).
Write a warm, professional closing statement (3-4 sentences) that:
1. Thanks the candidate for their time
2. Notes one genuinely positive aspect you observed
3. Tells them to click 'View Report' for detailed feedback"""
}
