import time
from services.llm import call_llm
from pydantic import BaseModel
from schemas.linkedin_score import (
    LinkedinHeadlineScoreResponse, 
    LinkedinAboutScoreResponse,
    LinkedinExperienceDescriptionResponse
)
from utils.promtps.headline import get_headline_prompt
from utils.promtps.about import get_about_prompt
from utils.promtps.experience import get_experience_description_prompt

async def get_headline_score(data):

    headline = data.get('profile', {}).get('headline', '')


    if not headline:
        return {
            "score": 0,
            "review": [{
                "check_type": "Headline Section",
                "passed": False,
                "message": "Headline section is missing"
            }]
        }

    system_message, prompt = get_headline_prompt(headline)


    analysis_result = await call_llm(
        system_message=system_message,
        prompt=prompt,
        response_model=LinkedinHeadlineScoreResponse   # Ensures the response matches the FixWithAITextResponse schema
    )

    # Check if analysis_result has the expected structure
    if "checks" not in analysis_result:
        # If validation failed, return error response
        error_msg = analysis_result.get('error', 'Unknown error')
        content_preview = analysis_result.get('content', '')[:200] if analysis_result.get('content') else 'No content'
        return {
            "score": 0,
            "review": [{
                "check_type": "Headline Analysis",
                "passed": False,
                "message": f"Failed to analyze headline. Error: {error_msg}"
            }]
        }

    weight = {
        "Professional Identity": 3.0,
        "Skills Integration": 3.0,
        "Searchability & Keywords": 3.0,
        "Formatting & Structure": 3.0
    }

    score = 0
    review = []
    
    # Process LLM checks and convert to new format
    for check in analysis_result["checks"]:
        review_item = {
            "check_type": check["check_type"],
            "passed": check["criteria_meet"],
            "message": check["remark"]
        }
        review.append(review_item)
        
        if check["criteria_meet"]:
            score += (weight[check["check_type"]])

    # Manual length check
    length_passed = False
    length_message = ""
    if len(headline) < 70:
        score += 1.5
        length_passed = False
        length_message = "Headline length is length too small lacks the clarity"
    elif len(headline) <= 150:
        score += 3.0
        length_passed = True
        length_message = "Headline is Length Optimal"
    else:
        score += 2.0
        length_passed = False
        length_message = "Headline length is too long and needs to be shortened"
    
    review.append({
        "check_type": "Length Optimization",
        "passed": length_passed,
        "message": length_message
    })

  

    return {
        "score": score,
        "review": review
    }



async def get_about_score(data):

    about = data.get("about", {}).get("text", "")

    if not about:
        return {
            "score": 0,
            "review": [{
                "check_type": "About Section",
                "passed": False,
                "message": "About section is missing"
            }]
        }


    system_message, prompt = get_about_prompt(about)
    
    result = await call_llm(
        system_message=system_message,
        prompt=prompt,
        response_model=LinkedinAboutScoreResponse   # Ensures the response matches the FixWithAITextResponse schema
    )

    # Check if result has the expected structure
    if "checks" not in result:
        # If validation failed, return error response
        error_msg = result.get('error', 'Unknown error')
        content_preview = result.get('content', '')[:200] if result.get('content') else 'No content'
        return {
            "score": 0,
            "review": [{
                "check_type": "About Section Analysis",
                "passed": False,
                "message": f"Failed to analyze about section. Error: {error_msg}"
            }]
        }

    weights = {
        "Professional Career Story": 3.0,
        "Skills and Strengths": 4.0,
        "Achievements and Impact": 4.0,
        "Human Touch": 3.0,
        "Call to Action": 3.0,
        "length" : 3.0
    }
    
    score = 0
    review = []
    
    # Process LLM checks and convert to new format
    for check in result["checks"]:
        review_item = {
            "check_type": check["check_type"],
            "passed": check["criteria_meet"],
            "message": check["remark"]
        }
        review.append(review_item)
        
        if check["criteria_meet"]:
            score += (weights.get(check["check_type"],0))

    # Manual length check
    about_length = len(about) if about else 0
    length_passed = False
    length_message = ""
    length_score = 0

    if about_length == 0:
        length_passed = False
        length_message = "About section is empty. Add a compelling summary to showcase your professional story"
        length_score = 0    
    elif about_length < 400:
        length_passed = False
        length_message = "About section length is below 400 characters."
        length_score = (weights["length"]/2)
    else:
        length_passed = True
        length_message = "About section length is 400 characters or more."
        length_score = weights["length"]

    score += length_score

    review.append({
        "check_type": "Length Optimization",
        "passed": length_passed,
        "message": length_message
    })

    return {
        "score": score,
        "review": review
    }


async def get_profile_content_score(data):
    """
    Evaluate profile content elements with flexible weightage system
    
    Weightage breakdown (adjustable):
    - Connections: 0.20 (20%)
    - Followers: 0.20 (20%)  
    - Name: 0.15 (15%)
    - Location: 0.15 (15%)
    - OpenToWork: 0.15 (15%)
    - OpenToWork Roles: 0.15 (15%)
    """
    
    # Flexible weightage system - easily adjustable
    weights = {
        "connections": 2.0,
        "followers": 2.0,
        "name": 2.0,
        "location": 1.0,
       "openToWork": 1.0,
        "openToWork_roles": 2.0
    }
    
    profile = data.get("profile", {})
    score = 0
    review = []
    
    import re

    def _is_detailed_location(loc):
        """
        Checks if the location string is in a detailed format like:
        'City, State, Country' (at least 3 comma-separated parts)
        and each part is non-empty and alphabetic (allowing spaces).
        """
        if not loc or not isinstance(loc, str):
            return False
        parts = [p.strip() for p in loc.split(",")]
        # At least 3 parts: city, state, country
        if len(parts) < 3:
            return False
        # All parts should be non-empty and contain at least one letter
        for part in parts:
            if not part or not re.search(r"[A-Za-z]", part):
                return False
        return True
    
    # 1. Connections check
    connections = profile.get("connections", 0)
    if connections >= 500:
        score += (weights["connections"] )
        review.append({
            "check_type": "Connections",
            "passed": True,
            "message": "Connections count is excellent (500+)"
        })
    elif connections > 100:
        score += (weights["connections"]/2)
        review.append({
            "check_type": "Connections",
            "passed": False,
            "message": "Connections count is moderate (100+). Add more professionals and peers to your network for better visibility"
        })
    else:
        score += 0
        review.append({
            "check_type": "Connections",
            "passed": False,
            "message": "Low connections count. Add more professionals and peers to your network to gain more visibility"
        })
    
    # 2. Followers check - if absent, use connections
    followers = profile.get("followers")
    if followers is not None:
        # Followers attribute is present
        if followers >= 250:
            score += (weights["followers"] )
            review.append({
                "check_type": "Followers",
                "passed": True,
                "message": "Followers count is excellent (250+)"
            })
        elif followers > 100:
            score += (weights["followers"]/2)
            review.append({
                "check_type": "Followers",
                "passed": False,
                "message": "Followers count is moderate (100+). Increase your followers by sharing valuable content and engaging with your network"
            })
        else:
            score += 0
            review.append({
                "check_type": "Followers",
                "passed": False,
                "message": "Low followers count. Increase your followers by sharing valuable content and engaging with your network"
            })
    else:
        # Followers attribute is absent, use connections
        if connections >= 250:
            score += (weights["followers"] )
            review.append({
                "check_type": "Followers",
                "passed": True,
                "message": "Network size is excellent (250+ connections)"
            })
        elif connections > 100:
            score += (weights["followers"]/2)
            review.append({
                "check_type": "Followers",
                "passed": False,
                "message": "Network size is moderate (100+ connections). Increase your network by connecting with more professionals in your field"
            })
        else:
            score += 0
            review.append({
                "check_type": "Followers",
                "passed": False,
                "message": "Small network size. Increase your network by connecting with more professionals in your field"
            })
    
    # 3. Name check
    name = profile.get("name", "")
    if name and name.strip():
        name_score = _check_name_format(name.strip())
        if name_score == 2:
            score += (weights["name"] )
            review.append({
                "check_type": "Name",
                "passed": True,
                "message": "Name is in professional format"
            })
        else:
            score += (weights["name"]/2)
            review.append({
                "check_type": "Name",
                "passed": False,
                "message": "Name needs improvement. Make sure your name is in professional format"
            })
    else:
        score += 0
        review.append({
            "check_type": "Name",
            "passed": False,
            "message": "Name is missing. Add your professional name to your profile"
        })
    
    # 4. Location check
    location = profile.get("location", "")
    if location and location.strip():
        if _is_detailed_location(location.strip()):
            score += (weights["location"] )
            review.append({
                "check_type": "Location",
                "passed": True,
                "message": "Location is present and detailed (e.g., City, State, Country)"
            })
        else:
            score += (weights["location"]/2)
            review.append({
                "check_type": "Location",
                "passed": False,
                "message": "Location is present but not detailed. Specify your location in the format 'City, State, Country' for better visibility"
            })
    else:
        score += 0
        review.append({
            "check_type": "Location",
            "passed": False,
            "message": "Location is missing. Add your location to help recruiters find you"
        })
    
    # 5. OpenToWork check
    open_to_work = profile.get("openToWork", {})
    if open_to_work.get("present", False):
        score += (weights["openToWork"] )
        review.append({
            "check_type": "Open To Work",
            "passed": True,
            "message": "OpenToWork is enabled - great for visibility to recruiters"
        })
    else:
        score += 0
        review.append({
            "check_type": "Open To Work",
            "passed": False,
            "message": "OpenToWork is not enabled. Enable this feature to signal to recruiters that you're actively seeking opportunities"
        })
    
    # 6. OpenToWork Roles check
    roles = open_to_work.get("roles", [])
    if len(roles) >= 5:
        score += (weights["openToWork_roles"] )
        review.append({
            "check_type": "Open To Work Roles",
            "passed": True,
            "message": "OpenToWork has 5+ job roles - excellent targeting"
        })
    elif len(roles) >= 3:
        score += (weights["openToWork_roles"]/2)
        review.append({
            "check_type": "Open To Work Roles",
            "passed": False,
            "message": "OpenToWork has 3+ job roles. Add more specific job roles for better targeting"
        })
    elif len(roles) > 0:
        score += (weights["openToWork_roles"]*0)
        review.append({
            "check_type": "Open To Work Roles",
            "passed": False,
            "message": "OpenToWork has some job roles. Add more specific job roles for better targeting"
        })
    else:
        score += 0
        review.append({
            "check_type": "Open To Work Roles",
            "passed": False,
            "message": "No job roles specified in OpenToWork. Add at least 5 specific job roles for optimal targeting"
        })
    
    return {
        "score": score,
        "review": review
    }



def _check_name_format(name):

    """
    Evaluate the format of a name:
    - 2 points: Professional format (proper case, valid structure)
    - 1 point: Basic format (somewhat valid)
    - 0 points: Invalid format
    """
    import re
    
    if not isinstance(name, str) or not name.strip():
        return 0

    name = name.strip()
    parts = [p for p in name.split() if p]
    if not parts:
        return 0

    prefixes = {"dr", "mr", "ms", "mrs", "miss", "prof", "sir", "madam", "shri", "smt"}
    suffixes = {"jr", "sr", "ii", "iii", "iv", "phd", "md", "esq"}

    clean = lambda x: x.lower().replace('.', '')

    # Remove prefix/suffix if present
    if clean(parts[0]) in prefixes:
        parts = parts[1:]
    if parts and clean(parts[-1]) in suffixes:
        parts = parts[:-1]
    if not parts:
        return 0

    # Updated pattern: allows "J" or "J."
    valid_pattern = re.compile(
        r"^(?:[A-Z][a-z]+|[A-Z]\.?|[A-Z][a-z]+[-'][A-Z][a-z]+|[A-Z][a-z]+\.)$"
    )

    # Validate each part
    if not all(valid_pattern.match(p) for p in parts):
        return 1  # basic format

    total_len = sum(len(p) for p in parts)
    if not (2 <= total_len <= 50):
        return 1

    if len(parts) > 5:
        return 1

    if not re.fullmatch(r"[A-Za-z\s'\-\.]+", name):
        return 1

    joined = ''.join(parts)
    if joined.isupper() or joined.islower():
        return 1

    return 2




async def get_experience_score(data):
    """
    Evaluate experience section and return score out of 10 points (average across all experience entries)
    
    For each experience entry, evaluate:
    - title (required, weight: 3)
    - from (required, weight: 2)
    - to (required, weight: 2)
    - duration (weight: 2)
    - location (weight: 3)
    - employment_type (weight: 3)
    - skills_used (weight: 2)
    - description (weight: 3, analyzed by LLM for role clarity and impact)
    """
    all_fields = {
        "title": {"weight": 3, "name": "Title"},
        "from": {"weight": 2, "name": "Start date"},
        "to": {"weight": 2, "name": "End date"},
        "duration": {"weight": 2, "name": "Duration"},
        "location": {"weight": 3, "name": "Location"},
        "employment_type": {"weight": 3, "name": "Employment Type"},
        "skills_used": {"weight": 2, "name": "Skills Used"},
        "description": {"weight": 3, "name": "Description"}
    }

    experience_list = data.get("experience", [])
    if not experience_list:
        return {
            "score": 0,
            "review": [{
                "check_type": "Experience Section",
                "passed": False,
                "message": "Experience section is missing"
            }]
        }

    experience_scores = []
    review = []

    for exp_index, experience in enumerate(experience_list):
        company_name = experience.get("company", "")
        experience_identifier = company_name if company_name else f"experience entry #{exp_index + 1}"

        if not company_name or not company_name.strip():
            review.append({
                "check_type": f"Experience Entry {exp_index + 1}",
                "passed": False,
                "message": "Company name is missing"
            })
            continue

        # Handle different role structures
        roles_data = []
        if "roles" in experience:
            roles_data = experience["roles"]
        elif "role" in experience:
            roles_data = [experience["role"]]

        if not roles_data:
            review.append({
                "check_type": f"Experience at {company_name}",
                "passed": False,
                "message": "Role information is missing"
            })
            continue

        for role_index, role in enumerate(roles_data):
            role_score = 0
            role_missing_fields = []
            role_title = role.get("title", "")
            if len(roles_data) > 1 and role_title:
                role_identifier = f"role '{role_title}' at {company_name}"
            elif role_title:
                role_identifier = f"role at {company_name}"
            else:
                role_identifier = f"role #{role_index + 1} at {company_name}" if len(roles_data) > 1 else f"role at {company_name}"

            for field, field_info in all_fields.items():
                field_value = role.get(field, "")

                if field == "description":
                    if field_value and str(field_value).strip():
                        try:
                            role_title_for_analysis = role.get("title", "Unknown Role")
                            system_message, prompt = get_experience_description_prompt(
                                field_value, role_title_for_analysis, company_name
                            )
                            
                            # Time tracking for LLM call
                            start_time = time.time()
                            if field_value.lower() not in ["not specified", "n/a", "na", ""]:

                              
                                analysis_result = await call_llm(
                                    system_message=system_message,
                                    prompt=prompt,
                                    response_model=LinkedinExperienceDescriptionResponse
                                )
                            else:
                                analysis_result = {
                                    "analysis": {
                                        "role_clarity": False,
                                        "impact_demonstrated": False
                                    }
                                }
                            end_time = time.time()
                            print(f"LLM call time for get_experience_description_score: {end_time - start_time:.2f} seconds")

                            analysis_data = analysis_result
                            analysis = analysis_data["analysis"]

                            description_score = 0
                            if analysis.get("role_clarity"):
                                description_score += field_info["weight"] / 2
                            if analysis.get("impact_demonstrated"):
                                description_score += field_info["weight"] / 2
                            role_score += description_score

                            missing_criteria = []
                            if not analysis.get("role_clarity"):
                                missing_criteria.append("role clarity")
                            if not analysis.get("impact_demonstrated"):
                                missing_criteria.append("impact demonstration")
                            if missing_criteria:
                                role_missing_fields.append(f"Description lacks {' and '.join(missing_criteria)}")
                        except Exception:
                            role_missing_fields.append("Description analysis failed")
                    else:
                        role_missing_fields.append(field_info["name"])
                elif field == "skills_used":
                    if isinstance(field_value, list) and len(field_value) > 0:
                        role_score += field_info["weight"]
                    elif isinstance(field_value, str) and field_value.strip():
                        role_score += field_info["weight"]
                    else:
                        role_missing_fields.append(field_info["name"])
                else:
                    if str(field_value).strip():
                        role_score += field_info["weight"]
                    else:
                        role_missing_fields.append(field_info["name"])

            experience_scores.append(role_score)
            if role_missing_fields:
                review.append({
                    "check_type": f"For {role_identifier}",
                    "passed": False,
                    "message": f"{', '.join(role_missing_fields)} {'is' if len(role_missing_fields) == 1 else 'are'} missing"
                })

    max_score_per_role = sum(field["weight"] for field in all_fields.values())
    total_score = sum(experience_scores) / len(experience_scores)
    final_score = round(total_score)


    return {
        "score": final_score,
        "review": review
    }


async def get_education_score(data):
    """
    Evaluate education section and return score out of 10 points (average across all education entries)
    
    For each education entry, evaluate:
    - college (required, weight: 1)
    - field_of_study (required, weight: 2)
    - from and to fields (required, weight: 2 each)
    - grade (optional, weight: 1)
    - skills_used (optional, weight: 2)
    """
    
    education_list = data.get("education", [])
    if not education_list:
        return {
            "score": 0,
            "review": [{
                "check_type": "Education Section",
                "passed": False,
                "message": "Education section is missing"
            }]
        }
    
    education_scores = []
    review = []
    
    for edu_index, education in enumerate(education_list):
        edu_score = 0
        edu_missing_fields = []
        
        # Get college name for identification
        college_name = education.get("college", "")
        study_type = education.get("study_type", "")
        education_identifier = college_name if college_name else f"education entry #{edu_index + 1}"
        education_identifier = f"{study_type} at {education_identifier}" if study_type else education_identifier
        
        # All fields with their weights
        all_fields = {
            "college_name": {"weight": 2, "name": "College"},
            "field_of_study": {"weight": 2, "name": "Field of Study"},
            "from": {"weight": 1, "name": "Start date"},
            "to": {"weight": 1, "name": "End date"},
            "grade": {"weight": 2, "name": "Grade"},
            "skills_used": {"weight": 2, "name": "Skills Used"}
        }
        
        # Check all fields
        for field, field_info in all_fields.items():
            field_value = education.get(field, "")
            
            # Special handling for skills_used (can be list or string)
            if field == "skills_used":
                if not field_value or (isinstance(field_value, list) and len(field_value) == 0) or (isinstance(field_value, str) and not field_value.strip()):
                    edu_missing_fields.append(field_info["name"])
                else:
                    edu_score += field_info["weight"]
            else:
                if field_value and str(field_value).strip() and str(field_value).lower() not in ["not specified", "n/a", "na", ""]:
                    edu_score += field_info["weight"]
                else:
                    edu_missing_fields.append(field_info["name"])
        
        # Only add to review if there are missing fields
        if edu_missing_fields:
            review.append({
                "check_type": f"For {education_identifier} college",
                "passed": False,
                "message": f"{', '.join(edu_missing_fields)} {'is' if len(edu_missing_fields) == 1 else 'are'} missing"
            })
        
        # Cap education score at 10
        edu_score = min(edu_score, 10)
        education_scores.append(edu_score)
    
    # Calculate overall score as average of all education scores
    overall_score = sum(education_scores) / len(education_scores) if education_scores else 0
    
    # Cap at 10 and round to 1 decimal place
    final_score = min(round(overall_score, 1), 10)
    
    return {
        "score": final_score,
        "review": review
    }


async def get_project_score(data):
    """
    Evaluate projects section and return score out of 10 points (average across all projects)
    
    For each project, evaluate:
    - title (weight: 2)
    - date (weight: 2)
    - description (weight: 3)
    - media links (weight: 3)
    """
    
    projects_list = data.get("projects", [])
    print(f"DEBUG: projects_list = {projects_list}")
    print(f"DEBUG: projects_list length = {len(projects_list) if projects_list else 0}")
    
    if not projects_list:
        return {
            "score": 0,
            "review": [{
                "check_type": "Projects Section",
                "passed": False,
                "message": "Projects section is missing"
            }]
        }
    
    project_scores = []
    review = []
    
    for proj_index, project in enumerate(projects_list):
        proj_score = 0
        proj_missing_fields = []
        
        # Get project title for identification
        project_title = project.get("title", "")
        project_identifier = project_title if project_title else f"project #{proj_index + 1}"
        
        # All fields with their weights
        all_fields = {
            "title": {"weight": 2, "name": "Title"},
            "date": {"weight": 2, "name": "Date"},
            "description": {"weight": 3, "name": "Description"},
            "media_links": {"weight": 3, "name": "Media Links"}
        }
        
        # Check title field
        if project_title and project_title.strip():
            proj_score += all_fields["title"]["weight"]
        else:
            proj_missing_fields.append("title")
        
        # Check date field
        project_date = project.get("date", "")
        if project_date and project_date.strip():
            proj_score += all_fields["date"]["weight"]
        else:
            proj_missing_fields.append("date")
        
        # Check description field using LLM evaluation
       
        description = project.get("description", "")
        if description and description.strip():
            try:
                # Use LLM to evaluate description quality
                description_evaluation = await _evaluate_project_description_with_llm(project_title, description)
                llm_score = description_evaluation["score"]
                llm_suggestion = description_evaluation["suggestion"]

                
                if llm_score >= 3:
                    # Score is 3 or above, add full weight (3 points)
                    proj_score += all_fields["description"]["weight"]
                else:
                    # Score is below 3, add the actual score and include suggestion
                    proj_score += llm_score
                    review.append({
                        "check_type": f"For {project_identifier} description",
                        "passed": False,
                        "message": f"{llm_suggestion}"
                    })

            except Exception as e:
                # Fallback scoring if LLM fails
                proj_score += all_fields["description"]["weight"]
        else:
            proj_missing_fields.append("description")
        
        # Check media links field
        media_links = []
        repo_link = project.get("repo_link", "")
        blog_link = project.get("blog_link", "")
        demo_link = project.get("demo_link", "")
        
        if repo_link and repo_link.strip():
            media_links.append("repository")
        if blog_link and blog_link.strip():
            media_links.append("blog/article")
        if demo_link and demo_link.strip():
            media_links.append("demo")
        
        if len(media_links) > 0:
            proj_score += all_fields["media_links"]["weight"]
        else:
            proj_missing_fields.append("media")
        
        # Only add to review if there are missing fields
        if proj_missing_fields:
            review.append({
                "check_type": f"For {project_identifier}",
                "passed": False,
                "message": f"{', '.join(proj_missing_fields)} {'is' if len(proj_missing_fields) == 1 else 'are'} missing"
            })
        
        # Cap project score at 10
        proj_score = min(proj_score, 10)
        project_scores.append(proj_score)
    
    # Calculate overall score as average of all project scores
    overall_score = sum(project_scores) / len(project_scores) if project_scores else 0
    
    # Cap at 10 and round to 1 decimal place
    final_score = min(round(overall_score, 1), 10)

    
    return {
        "score": final_score,
        "review": review
    }


async def _evaluate_project_description_with_llm(title, description):
    """
    Use LLM to evaluate project description quality and relevance
    Returns dict with score (1-5) and suggestion
    """
    from pydantic import BaseModel
    
    class ProjectDescriptionEvaluation(BaseModel):
        score: int  # 1-5 (overall quality score)
        suggestion: str  # One or two lines of improvement suggestions
    
    system_message = """
    You are a technical project evaluator. Analyze project descriptions for quality and provide improvement suggestions.
    Rate the description on a scale of 1-5 where:
    - 5: Excellent - Clear technical details, specific technologies, measurable outcomes
    - 4: Good - Well-structured with good technical content
    - 3: Average - Basic description with some technical details
    - 2: Below Average - Vague or lacks technical specifics
    - 1: Poor - Very basic or unclear description
    
    Provide concise suggestions for improvement.
    """
    
    prompt = f"""
    Evaluate this project description:
    
    Project Title: "{title}"
    Description: "{description}"
    
    Provide:
    - score (1-5): Overall quality rating based on technical depth, clarity, and specificity
    - suggestion: One or two lines of specific advice to improve the description
    
    Focus on: technical details, technologies used, measurable outcomes, and clarity.
    """
    
    try:
        # Time tracking for LLM call
     
        result = await call_llm(
            system_message=system_message,
            prompt=prompt,
            response_model=ProjectDescriptionEvaluation
        )
      
        # call_llm returns a dict, so access as dict
        score = result.get("score", 3)
        suggestion = result.get("suggestion", "Consider adding more technical details and measurable outcomes.")
        
        return {
            "score": max(1, min(score, 5)),  # Ensure score is between 1-5
            "suggestion": suggestion
        }
    except Exception as e:
        # Fallback scoring
        if len(description.strip()) > 100 and any(word in description.lower() for word in ['built', 'developed', 'created', 'implemented', 'designed']):
            return {"score": 3, "suggestion": "Consider adding more specific technical details and measurable outcomes."}
        elif len(description.strip()) > 50:
            return {"score": 2, "suggestion": "Add more technical details, technologies used, and specific achievements."}
        else:
            return {"score": 1, "suggestion": "Expand the description with technical details, technologies used, and project outcomes."}


async def get_skill_score(data):
    """
    Evaluate skills section with flexible weightage system
    
    Weightage breakdown (adjustable):
    - Skill count: 5 points
    - Endorsements: 3 points
    - Skill relevance: 2 points
    Total: 10 points
    """
    
    # Flexible weightage system - easily adjustable
    weights = {
        "skill_count": 5,
        "endorsements": 3,
        "skill_relevance": 2
    }
    
    skills_list = data.get("skills", [])
    if not skills_list:
        return {
            "score": 0,
            "review": [{
                "check_type": "Skills Section",
                "passed": False,
                "message": "Skills section is missing"
            }]
        }
    
    # Get headline for relevance checking
    headline = ""
    if "profile" in data:
        headline = data["profile"].get("headline", "")
    elif "headline" in data:
        headline = data.get("headline", "")
    
    review = []
    skill_score = 0
    
    # 1. Check total number of skills
    total_skills = len(skills_list)
    if total_skills >= 15:
        skill_score += weights["skill_count"]  # Full points
    else:
        skill_score += (total_skills / 15) * weights["skill_count"]  # Proportional scoring
        review.append({
            "check_type": "Skill count",
            "passed": False,
            "message": "Try to add alteast 15 skills to your skills section to increase your visibility"
        })
    
    # 2. Check endorsement levels
    low_endorsement_skills = []
    endorsement_score = 0
    
    for skill in skills_list:
        endorsements = skill.get("endorsements", 0)
        skill_name = skill.get("name", "Unknown skill")
        
        if endorsements >= 5:
            endorsement_score += 1  # Good endorsement level
        else:
            low_endorsement_skills.append(skill_name)
    
    # Calculate endorsement score
    if total_skills > 0:
        endorsement_percentage = endorsement_score / total_skills
        endorsement_points = endorsement_percentage * weights["endorsements"]
        skill_score += endorsement_points
        print(f"DEBUG: endorsement_score={endorsement_score}, endorsement_percentage={endorsement_percentage}, endorsement_points={endorsement_points}")
        
        # Add to review if endorsements are low
        if endorsement_percentage < 0.5:  # Less than 50% of skills have good endorsements
            skill_names = ", ".join(low_endorsement_skills[:5])  # Show first 5 skills
            if len(low_endorsement_skills) > 5:
                skill_names += " and others"
            review.append({
                "check_type": "Endorsements",
                "passed": False,
                "message": f"These skills ({skill_names}) have less endorsements, try to ask peers to endorse skills"
            })
    
    # 3. Check skills relevance to headline using LLM
    if headline:
        try:
            result = await _evaluate_skills_relevance_with_llm(headline, skills_list)
            relevance_score = result["relevance_score"]
            suggested_skills = result["suggested_skills"]
            
            if relevance_score >= 3:
                skill_score += weights["skill_relevance"]  # Full points
            else:
                skill_score += relevance_score / 5 * weights["skill_relevance"]  # Proportional scoring
                skills_list_text = ", ".join(suggested_skills)
                review.append({
                    "check_type": "Skill Relevance",
                    "passed": False,
                    "message": f"Consider adding these skills to your skill section: {skills_list_text}"
                })
        except Exception as e:
            # Fallback scoring if LLM fails
            skill_score += weights["skill_relevance"] * 0.6  # Assume 60% relevance
            review.append({
                "check_type": "Skill Relevance",
                "passed": False,
                "message": "Ensure your skills align with your professional headline and industry"
            })
    else:
        # No headline to compare against
        skill_score += weights["skill_relevance"] * 0.5  # 50% points
        review.append({
            "check_type": "Skill Relevance",
            "passed": False,
            "message": "Add a professional headline to better showcase how your skills align with your career focus"
        })
    
    # Cap final score at 10
    final_score = min(round(skill_score, 1), 10)
    
    return {
        "score": final_score,
        "review": review
    }


async def _evaluate_skills_relevance_with_llm(headline, skills_list):
    """
    Use LLM to evaluate how well skills align with the professional headline
    Returns suggested skills and relevance score
    """
    from pydantic import BaseModel
    from typing import List
    
    class SkillsRelevanceEvaluation(BaseModel):
        relevance_score: int         # 1-5 relevance score for current skills
        suggested_skills: List[str]  # 1-5 suggested in-demand skills to add
    
    system_message = """
    You are a career development expert specializing in LinkedIn profile optimization and industry trends. 
    Analyze how well a candidate's skills align with their professional headline and suggest high-demand, relevant skills.
    
    Focus on suggesting in-demand skills that are:
    - Currently trending in the industry
    - Highly sought after by recruiters
    - Relevant to the professional headline
    - Technical and industry-specific competencies
    """
    
    skills_text = ", ".join([skill.get("name", "") for skill in skills_list])
    
    prompt = f"""
    Evaluate skills relevance for this LinkedIn profile:
    
    Professional Headline: "{headline}"
    Listed Skills: {skills_text}
    
    Provide:
    - relevance_score (1-5): Rate how well the current skills align with the headline (1=poor alignment, 5=excellent alignment)
    - suggested_skills: List 3-5 specific IN-DEMAND skills that should be added to better match the headline and increase visibility to recruiters
    
    Focus on suggesting skills that are:
    - High-demand in the current job market for this profession
    - Technical skills that recruiters actively search for
    - Industry-specific competencies that are trending
    - Skills that would make the profile stand out to hiring managers
    
    Return exactly 3-5 suggested in-demand skills and a relevance score from 1-5.
    """
    
    try:
        # Time tracking for LLM call
      
      
        result = await call_llm(
            system_message=system_message,
            prompt=prompt,
            response_model=SkillsRelevanceEvaluation
        )
        
        # call_llm returns a dict, so access as dict
        return {
            "relevance_score": result.get("relevance_score", 3),
            "suggested_skills": result.get("suggested_skills", [])
        }
    except Exception as e:
        # Fallback scoring based on skill count and common patterns
        if len(skills_list) > 10:
            return {
                "relevance_score": 4,
                "suggested_skills": ["Communication", "Problem Solving", "Team Leadership"]
            }
        elif len(skills_list) >= 5:
            return {
                "relevance_score": 3,
                "suggested_skills": ["Communication", "Problem Solving", "Team Leadership", "Project Management"]
            }
        else:
            return {
                "relevance_score": 2,
                "suggested_skills": ["Communication", "Problem Solving", "Team Leadership", "Project Management", "Technical Writing"]
            }

async def get_certification_score(data):
    """
    Evaluate certifications section and return score out of 8 points (average across all certifications)
    
    For each certification, evaluate:
    - title (weight: 2)
    - provider (weight: 3)
    - issued_date (weight: 2)
    - skills_used (weight: 1)
    """
    
    certificates_list = data.get("certificates", [])
    if not certificates_list:
        return {
            "score": 0,
            "review": [{
                "check_type": "Certifications Section",
                "passed": False,
                "message": "Certifications section is missing"
            }]
        }
    
    certification_scores = []
    review = []
    
    for cert_index, certificate in enumerate(certificates_list):
        cert_score = 0
        cert_missing_fields = []
        
        # Get certificate title for identification
        cert_title = certificate.get("title", "")
        cert_identifier = cert_title if cert_title else f"certification #{cert_index + 1}"
        
        # All fields with their weights
        all_fields = {
            "title": {"weight": 2, "name": "Title"},
            "provider": {"weight": 3, "name": "Provider"},
            "issued_date": {"weight": 2, "name": "Issued Date"},
            "skills_used": {"weight": 1, "name": "Skills Used"}
        }
        
        # Check all fields
        for field, field_info in all_fields.items():
            field_value = certificate.get(field, "")
            
            # Special handling for skills_used (can be list or string)
            if field == "skills_used":
                if not field_value or (isinstance(field_value, list) and len(field_value) == 0) or (isinstance(field_value, str) and not field_value.strip()):
                    cert_missing_fields.append(field_info["name"])
                else:
                    cert_score += field_info["weight"]
            else:
                if field_value and str(field_value).strip():
                    cert_score += field_info["weight"]
                else:
                    cert_missing_fields.append(field_info["name"])
        
        # Only add to review if there are missing fields
        if cert_missing_fields:
            review.append({
                "check_type": f"{cert_identifier}",
                "passed": False,
                "message": f"{', '.join(cert_missing_fields)} {'is' if len(cert_missing_fields) == 1 else 'are'} missing"
            })
        
        # Cap certification score at 8
        cert_score = min(cert_score, 8)
        certification_scores.append(cert_score)
    
    # Calculate overall score as average of all certification scores
    overall_score = sum(certification_scores) / len(certification_scores) if certification_scores else 0
    
    # Cap at 8 and round to 1 decimal place
    final_score = min(round(overall_score, 1), 8)
    
    return {
        "score": final_score,
        "review": review
    }


async def get_volunteer_section_score(data):
    """
    Evaluate volunteering section and return score out of 2 points
    
    Scoring: 2 points if at least 1 volunteer experience is present, 0 points if none
    
    For each volunteer experience, check:
    - organization (required)
    - role (required)
    - from (required)
    - to (required)
    - type (optional but recommended)
    """
    
    volunteering_list = data.get("volunteering", [])
    if not volunteering_list:
        return {
            "score": 0,
            "review": [{
                "check_type": "Volunteering Section",
                "passed": False,
                "message": "Volunteering section is missing"
            }]
        }
    
    # Score: 2 points if at least 1 volunteer experience is present
    score = 2
    review = []
    
    for vol_index, volunteer in enumerate(volunteering_list):
        vol_missing_fields = []
        
        # Get organization and role for identification
        organization = volunteer.get("organization", "")
        role = volunteer.get("role", "")
        
        # Create identifier based on available information
        if role and organization:
            volunteer_identifier = f"{role} at {organization}"
        elif organization:
            volunteer_identifier = f"volunteer at {organization}"
        elif role:
            volunteer_identifier = f"{role}"
        else:
            volunteer_identifier = f"volunteer experience #{vol_index + 1}"
        
        # All fields to check with simplified names
        all_fields = {
            "organization": "Organization",
            "role": "Role",
            "from": "From",
            "to": "To",
            "type": "Type"
        }
        
        # Check all fields
        for field, field_name in all_fields.items():
            field_value = volunteer.get(field, "")
            if not (field_value and str(field_value).strip()):
                vol_missing_fields.append(field_name)
        
        # Only add to review if there are missing fields
        if vol_missing_fields:
            review.append({
                "check_type": f"{volunteer_identifier}",
                "passed": False,
                "message": f"{', '.join(vol_missing_fields)} {'is' if len(vol_missing_fields) == 1 else 'are'} missing"
            })
    
    return {
        "score": score,
        "review": review
    }

async def get_interest_section_score(data):
    """
    Evaluate interests section and return score out of 2 points
    
    Scoring: 2 points if at least 3 interest fields are present with content, 0 points otherwise
    
    Interest fields checked:
    - companies
    - groups  
    - newsletters
    - schools
    - topVoices
    """
    
    interests = data.get("interests", {})
    if not interests:
        return {
            "score": 0,
            "review": [
                {
                    "check_type": "Interest sections",
                    "passed": False,
                    "message": "Interests section is missing for your profile"
                }
            ]
        }
    
    # Count non-empty interest fields
    interest_fields = ["companies", "groups", "newsletters", "schools", "topVoices"]
    populated_fields = []
    empty_fields = []
    
    for field in interest_fields:
        field_value = interests.get(field, [])
        
        # Check if field has content
        if field_value:
            if isinstance(field_value, list) and len(field_value) > 0:
                populated_fields.append(field)
            elif isinstance(field_value, str) and field_value.strip():
                populated_fields.append(field)
        else:
            empty_fields.append(field)
    
    # Scoring: 2 points if at least 3 fields are populated
    score = 2 if len(populated_fields) >= 3 else 0
    passed = len(populated_fields) >= 3

    review = []
    if not passed:
        # Create message based on missing fields
        if empty_fields:
            if len(empty_fields) == 1:
                message = f"{empty_fields[0]} is missing"
            else:
                message = f"{', '.join(empty_fields)} are missing"
        else:
            message = "Not enough interest sections are present"
        review.append({
            "check_type": "Interest sections",
            "passed": False,
            "message": message
        })

    return {
        "score": score,
        "review": review
    }


async def get_language_score(data):
    """
    Evaluate languages section and return score out of 2 points
    
    Evaluation criteria:
    - At least 3 languages present (2 points)
    - Less than 3 languages present (0 points)
    - Check proficiency levels for suggestions
    """
    
    languages_list = data.get("languages", [])
    if not languages_list:
        return {
            "score": 0,
            "review": []
        }
    
    review = []
    language_score = 0
    
    # Check number of languages
    total_languages = len(languages_list)
    
    if total_languages >= 1:
        language_score = 2
    
    
    # Check proficiency levels for each language and add to review only those missing proficiency
    for language in languages_list:
        language_name = language.get("language", "Unknown Language")
        proficiency = language.get("proficiency", "").strip()
        
        if not proficiency or proficiency.lower() in ["", "not specified", "unknown"]:
            review.append({
                "check_type": "Language name",
                "passed": False,
                "message": "Proficiency is missing"
            })
    
    return {
        "score": language_score,
        "review": review
    }


async def get_profile_score(data):
    """
    Evaluate the profile pic
    """
    data1 = data.get("profile", {})
    profilePic = data1.get("profilePic", {})

    present = profilePic.get("present", False)
    isDefault = profilePic.get("isDefault", False)

    review = []

    if present:
        if isDefault:
            review.append({
                "check_type": "profile",
                "passed": False,
                "message": "Profile picture is using default image"
            })
            return {
                "score": 0,
                "review": review
            }
        else:
            return {
                "score": 10,
                "review": review
            }
    else:
        review.append({
            "check_type": "profile",
            "passed": False,
            "message": "Profile picture is missing"
        })
        return {
            "score": 0,
            "review": review
        }

async def get_banner_score(data):
    """
    Evaluate the banner
    """

    profile = data.get("profile", {})
    present = profile.get("banner",False)

    review = []


    if present:
            return {
                "score": 3,
                "review": review
            }
    else:
        review.append({
            "check_type": "banner",
            "passed": False,
            "message": "Banner is missing"
        })
        return {
            "score": 0,
            "review": review
        }

async def get_linkedin_url_score(data):
    """
    Evaluate the linkedin url and check if it's customized
    Returns 2 points if URL is customized, 1 points if not customized or missing
    """
    
    # Extract linkedin_url from profile data
    profile = data.get("profile", {})
    linkedin_url = profile.get("linkedin_url", "")
    
    review = []
    if not linkedin_url or not linkedin_url.strip():
        review.append({
            "check_type": "linkedin_url",
            "passed": False,
            "message": "LinkedIn URL is missing"
        })
        return {
            "score": 0,
            "review": review
        }
    
    # Check if URL is customized
    # A customized URL should contain "/in/" followed by a custom identifier (not random numbers)
    is_customized = False
    
    if "/in/" in linkedin_url:
        # Extract the part after "/in/"
        url_part = linkedin_url.split("/in/")[-1]
        # Remove any query parameters or fragments
        url_part = url_part.split("?")[0].split("#")[0]
        
        # Check if it contains only letters, numbers, hyphens, and underscores (custom format)
        # and doesn't contain only numbers (which would be a default LinkedIn ID)
        if url_part and not url_part.isdigit():
            # Additional check: should not be just random characters
            # A good custom URL typically has meaningful characters
            if len(url_part) > 2 and any(c.isalpha() for c in url_part):
                is_customized = True
    
    if is_customized:
        return {
            "score": 5,
            "review": review
        }
    else:
        review.append({
            "check_type": "linkedin_url",
            "passed": False,
            "message": "LinkedIn URL is not customized"
        })
        return {
            "score": 0,
            "review": review
        }

async def get_recommendation_score(data):
    """
    Evaluate recommendations section and return score out of 2 points
    
    Scoring criteria:
    - 2 points if 2 or more recommendations received
    - 1 point if 1 recommendation received
    - 0 points if no recommendations received
    - Use LLM to check clarity of recommendation text
    """
    
    recommendations = data.get("recommendations", {})
    received_recommendations = recommendations.get("received", [])
    given_recommendations = recommendations.get("given", [])
    
    # Calculate base score based on number of received recommendations
    num_received = len(received_recommendations)
    if num_received >= 2:
        base_score = 2
    elif num_received == 1:
        base_score = 1
    else:
        base_score = 0
    
    review = []
    
    # Only add checks when score is 1
    if base_score == 1:
        # Add Received Recommendations check
        review.append({
            "check_type": "Received Recommendations",
            "passed": False,
            "message": f"Received {num_received} recommendation(s) and try to add more recommendations and ask peers for recommendations"
        })
        
        # Get LLM suggestions and add Suggestions check
        try:
            clarity_suggestions = await _evaluate_recommendation_clarity_with_llm(received_recommendations)
            suggestions_message = ". ".join(clarity_suggestions)
        except Exception as e:
            # Fallback if LLM fails
            suggestions_message = "Ensure your recommendations are specific, detailed, and highlight concrete achievements"
        
        review.append({
            "check_type": "Suggestions",
            "passed": False,
            "message": suggestions_message
        })
    
    # Handle score 0 case
    if base_score == 0:
        review.append({
            "check_type": "Received Recommendations",
            "passed": False,
            "message": "Ask peers for recommendations"
        })
    
    return {
        "score": base_score,
        "review": review
    }


async def _evaluate_recommendation_clarity_with_llm(recommendations):
    """
    Use LLM to evaluate clarity and quality of recommendation text
    Returns suggestions for improvement
    """
    try:
        from pydantic import BaseModel
        from typing import List
        
        class RecommendationClarityEvaluation(BaseModel):
            suggestions: List[str]  # Suggestions for improving recommendation clarity
            overall_quality: str    # Overall assessment of recommendation quality
        
        system_message = """
        You are a LinkedIn profile optimization expert specializing in recommendation analysis.
        Evaluate the clarity, specificity, and impact of LinkedIn recommendations.
        
        Focus on:
        1. Impact - Are measurable results or outcomes mentioned?
        2. Professional tone - Is the language professional and credible?
        
        Provide actionable suggestions for improvement.
        """
        
        # Prepare recommendations text for analysis
        recommendations_text = ""
        for i, rec in enumerate(recommendations, 1):
            from_person = rec.get("from", "Unknown")
            position = rec.get("position", "Unknown Position")
            text = rec.get("text", "")
            recommendations_text += f"Recommendation {i}:\nFrom: {from_person} ({position})\nText: {text}\n\n"
        
        prompt = f"""
        Analyze these LinkedIn recommendations for clarity and quality:
        
        {recommendations_text}
        
        Provide:
        - suggestions: List 2-3 specific suggestions to improve recommendation clarity and impact
        - overall_quality: Brief assessment (e.g., "Good", "Needs Improvement", "Excellent")
        
        Focus on making recommendations more specific, measurable, and impactful.
        """
        
        # Suppress OpenAI errors from logs
        import warnings
        import logging
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            logging.getLogger("openai").setLevel(logging.ERROR)
            
          
           
            result = await call_llm(
                system_message=system_message,
                prompt=prompt,
                response_model=RecommendationClarityEvaluation
            )
           
        # call_llm returns a dict, so access as dict
        return result.get("suggestions", [])
        
    except Exception as e:
        # Fallback suggestions if LLM fails
        return [
            "Make recommendations more specific by mentioning concrete achievements",
            "Include measurable results or outcomes when possible",
            "Ensure recommendations highlight unique strengths and contributions"
        ]


async def get_activity_score(data):
    """
    Evaluate activity section and return score out of 2 points
    
    Scoring criteria:
    - 2 points if 2 or more posts
    - 1 point if 1 post
    - 0 points if no posts
    """
    
    activity = data.get("activity", {})
    posts = activity.get("posts", [])
    
    # Calculate score based on number of posts
    num_posts = len(posts)
    if num_posts >= 2:
        score = 2
    elif num_posts == 1:
        score = 1
    else:
        score = 0
    
    review = []
    
    # Add to review only when posts score is less than 2
    if score < 2:
        review.append({
            "check_type": "Number of Posts",
            "passed": False,
            "message": "Try to post more no of posts"
        })
    
    return {
        "score": score,
        "review": review
    }