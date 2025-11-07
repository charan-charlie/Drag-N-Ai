
def get_about_prompt(about_text):
    """
    Returns a system message and prompt for evaluating a LinkedIn About/Summary section
    according to best practices and professional storytelling standards.
    """
    system_message = """
    You are an expert LinkedIn profile reviewer and career coach specializing in professional storytelling and About section optimization.
    Your expertise includes understanding LinkedIn's search algorithm, recruiter preferences, and compelling narrative structure.
    You analyze About sections for engagement, professionalism, and search visibility following industry standards.
    
    ## Output Format:
    Return ONLY valid JSON (no markdown code blocks, no explanations, just the raw JSON object) with:
    - "overall_suggestion" (string): Comprehensive improvement advice for the about section
    - "checks" (array): List of evaluation criteria with results
    
    IMPORTANT: Do NOT wrap the JSON in markdown code blocks. Return pure JSON only.
    """

    prompt = f"""
    ## LinkedIn About Section to Analyze:
    "{about_text}"
  
    ## Evaluation Criteria:
    
    **1. Professional Career Story**
    - Clear explanation of who you are, your roles, and industries
    - Professional journey and expertise areas
    - Demonstrates career progression and focus

    **2. Skills and Strengths**
    - Mentions specific technical or soft skills
    - Skills are relevant to headline and searchable by recruiters


    **3. Achievements and Impact**
    - Does the About section contain ANY mention of achievements, results, impact, or accomplishments? Look for any form of success, growth, improvement, or value delivered. If any achievement is mentioned, mark this criteria as met (true). Do not evaluate strength or quality, only presence.
    - If it contains any achievements, results, or accomplishments (with any numbers, percentages, or scale), mark this criteria as met (true).

    **4. Human Touch**
    - Does the About section include any line showing passion, motivation, or personal qualities (e.g., adaptability, collaboration, continuous learning)?

    **5. Call to Action**
    - Does the About section contain ANY form of invitation, encouragement, or openness to connect, collaborate, discuss, share ideas, or explore opportunities? Look for phrases like "feel free to", "open to", "connect", "collaborate", "discuss", "share", "reach out", or similar expressions. If any such invitation exists, mark this criteria as met (true). Do not evaluate strength or quality, only presence.



    ## Additional Considerations
    - **Keywords**: Includes industry-relevant keywords for search visibility
    - **Readability**: Easy to scan with good flow and structure
    - **Tone**: Professional yet personable, appropriate for target audience

    ## Instructions:
    Analyze the About section against these criteria and provide comprehensive feedback focusing on what would make the about section more engaging and attractive to recruiters.

    ## Required JSON Output Format:
    {{
      "overall_suggestion": "Comprehensive improvement advice for the entire about section",
      "checks": [
        {{"check_type": "Professional Career Story", "criteria_meet": false, "remark": "Clear explanation of whether this criteria is met and why"}},
        {{"check_type": "Skills and Strengths", "criteria_meet": true, "remark": "Clear explanation of whether this criteria is met and why"}},
        {{"check_type": "Achievements and Impact", "criteria_meet": false, "remark": "Clear explanation of whether this criteria is met and why"}},
        {{"check_type": "Human Touch", "criteria_meet": true, "remark": "Clear explanation of whether this criteria is met and why"}},
        {{"check_type": "Call to Action", "criteria_meet": false, "remark": "Clear explanation of whether this criteria is met and why"}}
      ]
    }}
    """

    return system_message, prompt

