
def get_experience_description_prompt(description, role_title, company_name):
    """
    Returns a system message and prompt for evaluating experience description
    for role clarity and impact demonstration.
    """
    system_message = """
    You are an expert LinkedIn profile reviewer and career coach specializing in work experience optimization.
    Your expertise includes analyzing job descriptions for clarity, impact demonstration, and professional storytelling.
    You evaluate experience descriptions for recruiter appeal and professional credibility.
    
    ## Output Format:
    Return only a JSON object with analysis results.
    """

    prompt = f"""
    ## Experience Description to Analyze:
    Role: "{role_title}" at {company_name}
    Description: "{description}"

    ## Evaluation Criteria:
    
    **1. Role Clarity**
    - Does the description clearly explain what the person's role and responsibilities were?
    - Are the main duties and functions well-defined?
    - Would a recruiter understand what this person actually did in their job?
    - Avoid vague descriptions like "responsible for various tasks"

    **2. Impact Demonstrated**
    - Does the description show measurable results, achievements, or impact?
    - Are there specific examples of value delivered or problems solved?
    - Does it include quantifiable metrics (numbers, percentages, scale)?
    - Does it demonstrate how the person made a difference in their role?

    ## Instructions:
    Analyze the experience description against these two criteria. Determine if each criterion is met and provide specific feedback.

    ## Required JSON Output Format:
    {{
      "analysis": {{
        "role_clarity": true,
        "impact_demonstrated": false,
        "remark": "Detailed explanation of what's good and what needs improvement in the description"
      }}
    }}
    """

    return system_message, prompt
