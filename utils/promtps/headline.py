
def get_headline_prompt(headline):
    """
    Returns a system message and prompt for evaluating a LinkedIn headline
    according to best practices and recruiter-attracting patterns.
    """
    system_message = """
    You are an expert LinkedIn profile reviewer and career coach with extensive experience in professional branding and recruitment.
    Your expertise includes understanding LinkedIn's algorithm, recruiter search patterns, and headline optimization best practices.
    You analyze headlines for effectiveness, clarity, and recruiter appeal following industry standards.
    
    ## Output Format:
    Return ONLY valid JSON (no markdown code blocks, no explanations, just the raw JSON object) with:
    - "overall_suggestion" (string): Comprehensive improvement advice for the headline
    - "checks" (array): List of evaluation criteria with results
    
    IMPORTANT: Do NOT wrap the JSON in markdown code blocks. Return pure JSON only.
    """

    prompt = f"""
    ## LinkedIn Headline to Analyze:
    "{headline}"

    ## Evaluation Criteria:
    
    **1. Professional Identity (Weight: 25%)**
    - Must include current role/profession or target role
    - Should be specific, not generic (e.g., "Software Engineer" not "Professional")
    - Evaluate if the headline clearly communicates the person's professional identity

    **2. Skills Integration (Weight: 20%)**
    - Check if the headline includes 1 or 2 primary, relevant skills that recruiters search for

    **3. Searchability & Keywords (Weight: 15%)**
    - Contains industry keywords recruiters search for
    - Avoids meaningless buzzwords
    - Check if headline includes terms that improve LinkedIn search visibility

  
    **4. Formatting & Structure (Weight: 15%)**
    - Headline should use clear separators (such as "|", "•", "," , " or "-") between distinct sections (e.g., roles, certifications, skills, education, organizations).
    - Avoids using only spaces or inconsistent separators between sections.
    - Check for consistent and professional formatting (e.g., "Role | Certification | Skill | Education | Organization").

    ## Instructions:
    Analyze the headline against these criteria and provide comprehensive feedback focusing on what would make the headline more attractive to recruiters and improve LinkedIn search visibility.

    ## Required JSON Output Format:
    {{
      "overall_suggestion": "Comprehensive improvement advice for the entire headline",
      "checks": [
        {{"check_type": "Professional Identity", "criteria_meet": true, "remark": "Clear explanation of whether this criteria is met and why"}},
        {{"check_type": "Skills Integration", "criteria_meet": false, "remark": "Clear explanation of whether this criteria is met and why"}},
        {{"check_type": "Searchability & Keywords", "criteria_meet": true, "remark": "Clear explanation of whether this criteria is met and why"}},
        {{"check_type": "Formatting & Structure", "criteria_meet": true, "remark": "Clear explanation of whether this criteria is met and why"}}
      ]
    }}
    """

    return system_message, prompt
