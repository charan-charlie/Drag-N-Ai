
def get_headline_format(data):
    """
    Convert headline analysis data into the specified format
    """
    
    # Extract data from input
    score = data.get("score", 0)
    review = data.get("review", [])
    
    # Scale score to 100
    max_score = 15
    scaled_score = (score*(100/max_score))  # Scale from 0-10 to 0-100
    scaled_score = round(scaled_score)
    
    # Determine if it's a must-have (score >= 70)
    
    # Bonus tips related to LinkedIn Headline
    bonus_tips = [
        "Use industry-specific keywords that recruiters search for",
        "Include your current role or target position clearly",
        "Add relevant certifications or credentials",
        "Keep it range of 70 - 150 characters for optimal display",
        "Use symbols like | or • to separate different elements"
    ]
    
    # Additional info related to LinkedIn Headline tips
    additional_info = [
        "Your headline appears in search results and is the first thing people see",
        "A strong headline can increase your profile views by up to 40%",
        "Include 2-3 key skills that are relevant to your target role",
        "Avoid generic terms like 'Professional' or 'Experienced'",
        "Use action words to make your headline more dynamic",
        "Test different versions to see which performs better"
    ]
    
    
    return {
        "section": "headline",
        "title": "Headline",
        "description": "The headline effectively communicates the target role and relevant certifications, which is great for clarity and searchability",
        "score": str(scaled_score),
        "review": review,
        "bonus_tip": bonus_tips,
        "additional_info": additional_info,
    }


def get_about_format(data):

    """
    Convert about analysis data into the specified format
    """
    
    # Extract data from input
    score = data.get("score", 0)
    review = data.get("review", [])
    
    # Scale score to 100
    max_score = 20
    scaled_score = (score*(100/max_score))  # Scale from 0-10 to 0-100
    scaled_score = round(scaled_score)


    # Bonus tips related to LinkedIn About
    bonus_tips = [
        "Use your 'About' section to tell a compelling story about your career"
    ]

    additional_info = [
    "A strong 'About' section can engage recruiters and encourage them to reach out"
    ]

    return {
        "section": "about",
        "title": "About",
        "description" : "Your LinkedIn 'About' section is like a quick introduction. It's your chance to tell people who you are, what you're good at, and what you're looking for—all in your own words",
        "score": str(scaled_score),
        "review": review,
        "bonus_tip": bonus_tips,
        "additional_info": additional_info
    }


def get_experience_format(data):
    """
    Convert experience analysis data into the specified format
    """
    score = data.get("score", 0)
    review = data.get("review", [])


    max_score = 20

    scaled_score = (score*(100/max_score))
    scaled_score = round(scaled_score)


    bonus_tip = ["Use numbers and quantifiable results to highlight your achievements"]
    additional_info = ["Detailed experience sections with skills and descriptions increase your chances of appearing in relevant job searches"]

    if score == max_score:
        review = [{
            "check_type": "Experience",
            "passed": True,
            "message": "Everything is perfect and you have done great job"
        }]
        return {
            "section": "experience",
            "score": str(scaled_score),
            "title": "Experience",
            "description": "Detailed descriptions of your professional roles and accomplishments",
            "review": review,
            "bonus_tip": bonus_tip,
            "additional_info": additional_info,
        }
    else:
        return {
            "section": "experience",
            "score": str(scaled_score),
            "title": "Experience",
            "description": "Detailed descriptions of your professional roles and accomplishments",
            "review": review,
            "bonus_tip": bonus_tip,
            "additional_info": additional_info,
        }

def get_education_format(data):

    """
    Convert education analysis data into the specified format
    """
    score = data.get("score", 0)
    review = data.get("review", [])
    
    max_score = 10
    scaled_score = (score*(100/max_score))
    scaled_score = round(scaled_score)

    
    bonus_tip = ["Include any special achievements or honors in your education section"]
    additional_info = ["Detailed education sections make your profile more compelling to employers"]
    
    if score == max_score:
        review = [{
            "check_type": "Education",
            "passed": True,
            "message": "Everything is perfect and you have done great job Buddy 😁"
        }]
        return {
            "section": "education",
            "score": str(scaled_score),
            "title": "Education",
            "description": "Detailed descriptions of your educational background",
            "review": review,
            "bonus_tip": bonus_tip,
            "additional_info": additional_info,
        }
    else:
        return {
            "section": "education",
            "score": str(scaled_score),
            "title": "Education",
            "description": "Detailed descriptions of your educational background",
            "review": review,
            "bonus_tip": bonus_tip,
            "additional_info": additional_info,
        }


def get_project_format(data):
    """
    Convert project analysis data into the specified format
    """
    score = data.get("score", 0)
    review = data.get("review", [])

    max_score = 10
    scaled_score = (score*(100/max_score))
    scaled_score = round(scaled_score)
    # Use checks as check_lis
    
    bonus_tip = ["Make sure each project is linked to your relevant experience"]
    additional_info = ["Projects can showcase your hands-on experience and abilities"]
    
    if score == max_score:
        review = [{
            "check_type": "Projects",
            "passed": True,
            "message": "Everything is seems good and you are good with your projects 😉"
        }]
        return {
            "section": "projects",
            "score": str(scaled_score),
            "title": "Projects",
            "description": "Detailed descriptions of your projects",
            "review" : review,
            "bonus_tip": bonus_tip,
            "additional_info": additional_info
        }
    else:
        return {
            "section": "projects",
            "score": str(scaled_score),
            "title": "Projects",
            "description": "Detailed descriptions of your projects",
            "review" : review,
            "bonus_tip": bonus_tip,
            "additional_info": additional_info
        }

def get_skill_format(data):
    """
    conver skill analyised into specifed format
    """
    score = data.get("score", 0)
    review = data.get("review", [])


    max_score = 10
    scaled_score = (score*(100/max_score))
    scaled_score = round(scaled_score)

    
    bonus_tip = ["Endorsements from colleagues and connections can boost your skills' visibility"]
    additional_info = ["Profiles with more skills often appear in more searches"]
    
    if score == max_score:
        review = [{
            "check_type": "Skills",
            "passed": True,
            "message": "You have very good skills set, Keep upskilling 🚀"
        }]
        return {
            "section": "skills",
            "score": str(scaled_score),
            "title": "Skills",
            "description": "Highlight your top skills and competencies",
            "review" : review,
            "bonus_tip": bonus_tip,
            "additional_info": additional_info
        }
    else:
        return {
            "section": "skills",
            "score": str(scaled_score),
            "title": "Skills",
            "description": "Highlight your top skills and competencies",
            "review" : review,
            "bonus_tip": bonus_tip,
            "additional_info": additional_info
        }



def get_certification_format(data):
    """
    convert certification analyised into specifed format
    """
    score = data.get("score", 0)
    review = data.get("review",[])

    max_score = 8
    scaled_score = (score*(100/max_score))
    scaled_score = round(scaled_score)
   
    
    additional_info = ["Profiles with certifications appear more credible and capable"]
    bonus_tip = ["Certifications demonstrate your commitment to professional development"]
    
    if score == max_score and not review:
        review = [{
            "check_type": "Certifications",
            "passed": True,
            "message": "You got certificate for keeping all required fields present"
        }]
        return {
            "section": "certificates",
            "score": str(scaled_score),
            "title": "Certifications",
            "description": "Highlight your certifications and credentials",
            "review" : review,
            "bonus_tip": bonus_tip,
            "additional_info": additional_info
        }
    else:
        return {
            "section": "certificates",
            "score": str(scaled_score),
            "title": "Certifications",
            "description": "Highlight your certifications and credentials",
            "review" : review,
            "bonus_tip": bonus_tip,
            "additional_info": additional_info
        }


def get_volunteer_format(data):
    """
    convert volunteer analyised into specifed format
    """
    score = data.get("score", 0)
    review = data.get("review", [])
  
    
    max_score = 2
    scaled_score = (score*(100/max_score))
    scaled_score = round(scaled_score)
 
    
    bonus_tip = ["Volunteering experience can help strengthen your profile if relevant to your career"]
    additional_info = ["Volunteer work can demonstrate your values and transferable skills"]
    
    if score == max_score and not review:
        review = [{
            "check_type": "volunteering",
            "passed": True,
            "message": "Everything is perfect and you have done great job Buddy "
        }]  
        return {
            "section": "volunteering",
            "score": str(scaled_score),
            "title": "Volunteer",
            "description": "Demonstrate your commitment to causes and communities",
            "review" : review,
            "bonus_tip": bonus_tip,
            "additional_info": additional_info
        }
    else:
        return {
            "section": "volunteering",
            "score": str(scaled_score),
            "title": "Volunteer",
            "description": "Demonstrate your commitment to causes and communities",
            "review" : review,
            "bonus_tip": bonus_tip,
            "additional_info": additional_info
        }

def get_interest_format(data):
    """
    convert interest analyised into specifed format
    """
    score = data.get("score", 0)
    review = data.get("review", [])
   

    max_score = 2
    scaled_score = (score*(100/max_score))
    scaled_score = round(scaled_score)
 
    
    bonus_tip = ["Include a mix of professional, personal, and industry-specific interests"]
    additional_info = ["Interests show your engagement and passions beyond work"]
    
    if score == max_score and not review:
        review = [{
            "check_type": "Interests",
            "passed": True,
            "message": "Everything is seems good"
        }]
        return {
            "section": "interests",
            "score": str(scaled_score),
            "title": "Interests",
            "description": "Demonstrate your engagement and passions beyond work",
            "review" : review,
            "bonus_tip": bonus_tip,
            "additional_info": additional_info
        }
    else:
        return {
            "section": "interests",
            "score": str(scaled_score),
            "title": "Interests",
            "description": "Demonstrate your engagement and passions beyond work",
            "review" : review,
            "bonus_tip": bonus_tip,
            "additional_info": additional_info
        }

def get_language_format(data):
    """
    convert language anaylised into specified format
    """

    score = data.get("score",0)
    review = data.get("review",[])
  

    max_score = 2
    scaled_score = (score*(100/max_score))
    scaled_score = round(scaled_score)


    bonus_tip = ["Fluency in multiple languages can make you more attractive to global employers"]
    additional_info = ["Multilingual profiles often stand out in global job markets"]



    if score == max_score and not review:
        review = [{
            "check_type": "Languages",
            "passed": True,
            "message": "Hey Champ!, All are perfect"
        }]  
        return {
            "section": "languages",
            "score": str(scaled_score),
            "title": "Languages",
            "description": "Demonstrate your language proficiency",
            "review" : review,
            "bonus_tip": bonus_tip,
            "additional_info": additional_info
        }
    else:
        return {
            "section": "languages",
            "score": str(scaled_score),
            "title": "Languages",
            "description": "Demonstrate your language proficiency",
            "review" : review,
            "bonus_tip": bonus_tip,
            "additional_info": additional_info
        }


def get_profile_format(data):

    """
    convert profile analyised into specified format
    """
    score = data.get("score",0)
    review = data.get("review",[])

    max_score = 10
    scaled_score = (score*(100/max_score))
    scaled_score = round(scaled_score)
   


    bonus_tip = ["Smile and make eye contact with the camera for a more approachable look"]
    additional_info = ["A professional photo can help your profile stand out and reinforce your personal brand","LinkedIn profiles with professional photos are 14 times more likely to be viewed"]
    

    if score == max_score:
        review = [{
            "check_type": "Profile Content",
            "passed": True,
            "message": "Profile picture is present and make sure you have smile on your face 😁"
        }]
        return {
            "section": "profile_pic",
            "score": str(scaled_score),
            "title": "Profile Content",
            "description": "Key elements of your LinkedIn profile to ensure a strong first impression",
            "review" : review,
            "bonus_tip": bonus_tip,
            "additional_info": additional_info,
        }
    else:
        return {
            "section": "profile_pic",
            "score": str(scaled_score),
            "title": "Profile Content",
            "description": "Key elements of your LinkedIn profile to ensure a strong first impression",
            "review" : review,
            "bonus_tip": bonus_tip,
            "additional_info": additional_info,
        }


def get_banner_format(data):
    """
    convert banner analyised into specified format
    """
    score = data.get("score",0)
    review = data.get("review",[])
    

    max_score = 3
    scaled_score = (score*(100/max_score))
    scaled_score = round(scaled_score)
    
    bonus_tip = ["Use a tool like Canva to create a professional-looking banner"]
    additional_info = ["A custom banner image can increase profile views by up to 11%","Your banner image is an opportunity to showcase your personality or professional achievements"]
    
    if score == max_score:
        review = [{
            "check_type": "Banner",
            "passed": True,
            "message": "Banner is present and promte your brand or your characterstics on banner image 😉"
        }]
        return {
            "section": "profile_bg_pic",
            "score": str(scaled_score),
            "title": "Banner",
            "description": "Showcase your personality and brand",
            "review" : review,
            "bonus_tip": bonus_tip,
            "additional_info": additional_info
        }
    else:
        return {
            "section": "profile_bg_pic",
            "score": str(scaled_score),
            "title": "Banner",
            "description": "Showcase your personality and brand",
            "review" : review,
            "bonus_tip": bonus_tip,
            "additional_info": additional_info
        }

def get_linkedin_url_format(data):
    """
    convert linkedin url analyised into specified format
    """
    score = data.get("score",0)
    review = data.get("review",[])
    
    max_score = 5
    scaled_score = (score*(100/max_score))
    scaled_score = round(scaled_score)
    
    bonus_tip = ["Customize your LinkedIn URL to make it more professional (e.g., linkedin.com/in/yourname)"]
    additional_info = ["A custom LinkedIn URL can increase profile views by up to 11%","Your LinkedIn URL is an opportunity to showcase your personality or professional achievements"]
    
    if score == max_score:
        review = [{
            "check_type": "LinkedIn URL",
            "passed": True,
            "message": "Yoh have customized Linkedin Url perfect!"
        }]
        return {
            "section": "linkedin_url",
            "score": str(scaled_score),
            "title": "LinkedIn URL",
            "description": "Ensure your LinkedIn URL is customized and professional",
            "review" : review,
            "bonus_tip": bonus_tip,
            "additional_info": additional_info
        }
    else:
        return {
            "section": "linkedin_url",
            "score": str(scaled_score),
            "title": "LinkedIn URL",
            "description": "Ensure your LinkedIn URL is customized and professional",
            "review" : review,
            "bonus_tip": bonus_tip,
            "additional_info": additional_info
        }

def get_recommendation_format(data):
    """
    convert recommendation analyised into specified format
    """
    score = data.get("score",0)
    review = data.get("review",[])
    
    max_score = 2
    scaled_score = (score*(100/max_score))
    scaled_score = round(scaled_score)
    
    bonus_tip = [" A single detailed recommendation from a senior leader often holds more weight than multiple generic ones from peers."]
    additional_info = ["Recommendations that specifically mention projects, results, and soft skills provide concrete proof of your abilities."," Actively request recommendations from managers, clients, or senior colleagues right after completing a significant project while your contribution is fresh in their mind."]
    
    if score == max_score and not review:
        review = [{
            "check_type": "Recommendations",
            "passed": True,
            "message": "Everything is perfect !"
        }]
        return {
            "section": "recommendations",
            "score": str(scaled_score),
            "title": "Recommendations",
            "description": "Showcase your professional engagement and industry connections",
            "review": review,
            "bonus_tip": bonus_tip,
            "additional_info": additional_info
        }
    else:
        return {
            "section": "recommendations",
            "score": str(scaled_score),
            "title": "Recommendations",
            "description": "Showcase your professional engagement and industry connections",
            "review": review,
            "bonus_tip": bonus_tip,
            "additional_info": additional_info
        }

def get_profile_content_format(data):
    """
    convert profile content analyised into specified format
    """
    score = data.get("score",0)
    review = data.get("review",[])
    
    max_score = 10
    scaled_score = (score*(100/max_score))
    scaled_score = round(scaled_score)
    
    bonus_tip = ["Add more professional and peers to your network in order to gain more visibility"]
    additional_info = ["Recruiters use advanced search filters that rely heavily on these specific data points—like your location, 'Open to Work' status, and job titles—to quickly narrow down candidate pools", "An incomplete or inaccurate profile content section means you're often invisible in these critical searches, no matter how qualified you are"]

    return {
        "section": "profile",
        "score": str(scaled_score),
        "title": "Profile Content",
        "description": "Key elements of your LinkedIn profile to ensure a strong first impression",
        "review" : review,
        "bonus_tip": bonus_tip,
        "additional_info": additional_info,

    }

def get_activity_format(data):
    """
    convert activity analyised into specified format
    """
    score = data.get("score",0)
    review = data.get("review",[])
    
    max_score = 2
    scaled_score = (score*(100/max_score))
    scaled_score = round(scaled_score)
    
    bonus_tip = ["Share relevant content regularly to keep your profile active"]
    additional_info = ["Regular content sharing can help you stay top of mind with recruiters and potential employers"]
    
    if score == max_score and not review:
        review = [{
            "check_type": "Activity",
            "passed": True,
            "message": "You have posted more than 2 posts and you are active on LinkedIn keep it up 🚀"
        }]
        return {
            "section": "activity",
            "score": str(scaled_score),
            "title": "Activity",
            "description": "Showcase your professional engagement and industry connections",
            "review": review,
            "bonus_tip": bonus_tip,
            "additional_info": additional_info
        }
    else:
        return {
            "section": "activity",
            "score": str(scaled_score),
            "title": "Activity",
            "description": "Showcase your professional engagement and industry connections",
            "review": review,
            "bonus_tip": bonus_tip,
            "additional_info": additional_info
        }

    

