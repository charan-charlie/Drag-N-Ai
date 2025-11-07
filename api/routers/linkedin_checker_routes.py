from uuid import UUID
import json
import asyncio
import re
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Dict, Any, List, AsyncGenerator
from models.user_linkedin_profile import UserLinkedInProfile
from models.user import User
from models.linkedin_profile import LinkedInProfile
from database import get_db


from utils.scorer.linkedin_score import get_profile_score
from utils.scorer.linkedin_score import get_headline_score
from utils.scorer.linkedin_score import get_about_score
from utils.scorer.linkedin_score import get_profile_content_score
from utils.scorer.linkedin_score import get_experience_score
from utils.scorer.linkedin_score import get_education_score
from utils.scorer.linkedin_score import get_project_score
from utils.scorer.linkedin_score import get_skill_score
from utils.scorer.linkedin_score import get_certification_score
from utils.scorer.linkedin_score import get_volunteer_section_score
from utils.scorer.linkedin_score import get_interest_section_score
from utils.scorer.linkedin_score import get_language_score
from utils.scorer.linkedin_score import get_profile_content_score
from utils.scorer.linkedin_score import get_banner_score
from utils.scorer.linkedin_score import get_linkedin_url_score
from utils.scorer.linkedin_score import get_recommendation_score
from utils.scorer.linkedin_score import get_activity_score
from utils.linkedin_format.linkedin_format import get_headline_format
from utils.linkedin_format.linkedin_format import get_about_format
from utils.linkedin_format.linkedin_format import get_experience_format
from utils.linkedin_format.linkedin_format import get_education_format
from utils.linkedin_format.linkedin_format import get_project_format
from utils.linkedin_format.linkedin_format import get_skill_format
from utils.linkedin_format.linkedin_format import get_certification_format
from utils.linkedin_format.linkedin_format import get_volunteer_format
from utils.linkedin_format.linkedin_format import get_interest_format
from utils.linkedin_format.linkedin_format import get_language_format
from utils.linkedin_format.linkedin_format import get_banner_format
from utils.linkedin_format.linkedin_format import get_profile_format
from utils.linkedin_format.linkedin_format import get_linkedin_url_format
from utils.linkedin_format.linkedin_format import get_recommendation_format
from utils.linkedin_format.linkedin_format import get_profile_content_format
from utils.linkedin_format.linkedin_format import get_activity_format



router = APIRouter()

async def process_sections_streaming(data: Dict[str, Any], user_id: UUID, db: AsyncSession) -> AsyncGenerator[str, None]:
    """
    Process LinkedIn profile sections and stream results as they complete
    """
    try:
        # Initialize total score
        total_score = 0
        completed_sections = []
        
        # Define section processing order and metadata
        sections_config = [
            {
                "name": "profile_content",
                "scorer": get_profile_content_score,
                "formatter": get_profile_content_format,
                "display_name": "Profile Content"
            },
            {
                "name": "profile_pic",
                "scorer": get_profile_score,
                "formatter": get_profile_format,
                "display_name": "Profile Picture"
            },
            {
                "name": "banner",
                "scorer": get_banner_score,
                "formatter": get_banner_format,
                "display_name": "Banner"
            },
            {
                "name": "headline", 
                "scorer": get_headline_score,
                "formatter": get_headline_format,
                "display_name": "Headline"
            },
            {
                "name": "about",
                "scorer": get_about_score,
                "formatter": get_about_format,
                "display_name": "About Section"
            },
            {
                "name": "experience",
                "scorer": get_experience_score,
                "formatter": get_experience_format,
                "display_name": "Experience"
            },
            {
                "name": "education",
                "scorer": get_education_score,
                "formatter": get_education_format,
                "display_name": "Education"
            },
            {
                "name": "projects",
                "scorer": get_project_score,
                "formatter": get_project_format,
                "display_name": "Projects"
            },
            {
                "name": "skills",
                "scorer": get_skill_score,
                "formatter": get_skill_format,
                "display_name": "Skills"
            },
            {
                "name": "certifications",
                "scorer": get_certification_score,
                "formatter": get_certification_format,
                "display_name": "Certifications"
            },
            {
                "name": "volunteering",
                "scorer": get_volunteer_section_score,
                "formatter": get_volunteer_format,
                "display_name": "Volunteering"
            },
            {
                "name": "interests",
                "scorer": get_interest_section_score,
                "formatter": get_interest_format,
                "display_name": "Interests"
            },
            {
                "name": "languages",
                "scorer": get_language_score,
                "formatter": get_language_format,
                "display_name": "Languages"
            },
            {
                "name": "linkedin_url",
                "scorer": get_linkedin_url_score,
                "formatter": get_linkedin_url_format,
                "display_name": "LinkedIn URL"
            },
            {
                "name": "recommendations",
                "scorer": get_recommendation_score,
                "formatter": get_recommendation_format,
                "display_name": "Recommendations"
            },
            {
                "name": "activity",
                "scorer": get_activity_score,
                "formatter": get_activity_format,
                "display_name": "Activity"
            }
        ]
        
        # Send initial response
       

        # Process each section
        for section_config in sections_config:
            try:
                # Get score
                score_result = await section_config["scorer"](data)
                
                # Format result
                formatted_result = section_config["formatter"](score_result)
                
                # Update total score
                sections_to_include_in_total = ["profile_pic","profile_content", "headline", "about","experience", "education", "skills", "linkedin_url"]
                if section_config["name"] in sections_to_include_in_total:
                    section_score = score_result.get("score", 0)
                    total_score += section_score
                
                # Add to completed sections
                completed_sections.append(formatted_result)

                stream = round(total_score)
                
                # Send section result
                section_response = {
                    "message_type" : "section_analysis",
                    "score": stream,
                    "sections": [formatted_result]
                }
                
                yield f"data: {json.dumps(section_response)}\n\n"
                
                
            except Exception as e:
                # Send error for this section
                error_response = {
                    "message_type": "error",
                    "section_name": section_config["name"],
                    "display_name": section_config["display_name"],
                    "error": str(e),
                    "total_score": total_score,
                    "progress": len(completed_sections),
                    "total_sections": len(sections_config),
                    "message": "Analysis failed"
                }
                yield f"data: {json.dumps(error_response)}\n\n"
        
        # Send final response
        final_response = {
            "message_type": "complete_analysis",
            "score": round(total_score),
            "sections": completed_sections
        }
        
        # Store in database
        try:
            # Get LinkedIn URL from data if available
            linkedin_url = data.get("profile", {}).get("linkedin_url", "")
            
            # Check if user already has a record in user_linkedin_profile table
            user_profile_query = select(UserLinkedInProfile).where(UserLinkedInProfile.user_id == user_id)
            existing_user_profile = await db.scalar(user_profile_query)
            
            if existing_user_profile:
                # User is doing analysis for the second time
                # Update the linkedin_profile table
                linkedin_profile_query = select(LinkedInProfile).where(LinkedInProfile.profile_url == existing_user_profile.linkedin_profile_url)
                existing_linkedin_profile = await db.scalar(linkedin_profile_query)
                
                if existing_linkedin_profile:
                    # Update existing linkedin_profile record
                    existing_linkedin_profile.profile_data = data
                    existing_linkedin_profile.profile_report_data = final_response
                    
                    # Update profile_url if it has changed
                    if linkedin_url and linkedin_url != existing_linkedin_profile.profile_url:
                        existing_linkedin_profile.profile_url = linkedin_url
                        # Update the user_linkedin_profile table with new URL
                        existing_user_profile.linkedin_profile_url = linkedin_url
                else:
                    
                    new_linkedin_profile = LinkedInProfile(
                        profile_url=linkedin_url,
                        profile_data=data,
                        profile_report_data=final_response
                    )
                    db.add(new_linkedin_profile)
                    
                    # Update user_linkedin_profile with new URL
                    existing_user_profile.linkedin_profile_url = linkedin_url
            else:
                
                # Check if linkedin_profile already exists with this URL
                linkedin_profile_query = select(LinkedInProfile).where(LinkedInProfile.profile_url == linkedin_url)
                existing_linkedin_profile = await db.scalar(linkedin_profile_query)
                
                if existing_linkedin_profile:
                    # Update existing linkedin_profile record
                    existing_linkedin_profile.profile_data = data
                    existing_linkedin_profile.profile_report_data = final_response
                else:
                    # Create new linkedin_profile record
                    new_linkedin_profile = LinkedInProfile(
                        profile_url=linkedin_url,
                        profile_data=data,
                        profile_report_data=final_response
                    )
                    db.add(new_linkedin_profile)
                
                # Create new user_linkedin_profile record
                new_user_profile = UserLinkedInProfile(
                    user_id=user_id,
                    linkedin_profile_url=linkedin_url
                )
                db.add(new_user_profile)
            
            await db.commit()
           
            
                
        except Exception as e:
            # Log error but don't fail the response
            print(f"Error saving to database: {e}")
            await db.rollback()
        
        yield f"data: {json.dumps(final_response)}\n\n"
        


    except Exception as e:
        # Send error response
        error_response = {
            "message_type": "error",
            "error": str(e),
            "message": "Analysis failed"
        }
        yield f"data: {json.dumps(error_response)}\n\n"

@router.post("/user/{user_id}/linkedin-checker/profile/stream")
async def check_linkedin_profile_stream(user_id: UUID, data: Dict[str, Any], db: AsyncSession = Depends(get_db)):
    """
    Stream LinkedIn profile analysis results as they complete
    
    Args:
        data: LinkedIn profile data in JSON format containing profile sections
    
    Returns:
        Server-Sent Events stream containing:
            - Individual section results as they complete
            - Progress updates
            - Final complete result
    """
    try:
        # Validate input data
        if not data:
            raise HTTPException(status_code=400, detail="Profile data is required")
        
        return StreamingResponse(
            process_sections_streaming(data, user_id, db),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/linkedin-checker/profile")
async def check_linkedin_profile(data: Dict[str, Any]):
    """
    Analyze and score a LinkedIn profile with AI-powered suggestions
    
    Args:
        data: LinkedIn profile data in JSON format containing profile sections
    
    Returns:
        Dict containing:
            - score_data: Overall profile score
            - sections: Detailed analysis and suggestions for each section
    """
    try:
        # Initialize analyzers
      
        
        # Validate input data
        if not data:
            raise HTTPException(status_code=400, detail="Profile data is required")

        
        profile_data = data.get('profile', {})


        headline_result =  await get_headline_score(profile_data.get('headline', ''))
        profile_content_result = await get_profile_content_score(data)
        about_result =  await get_about_score(data)
        experience_result = await get_experience_score(data)
        education_result = await get_education_score(data)
        project_result = await get_project_score(data)
        skill_result = await get_skill_score(data)
        certification_result = await get_certification_score(data)
        volunteer_result = await get_volunteer_section_score(data)
        interest_result = await get_interest_section_score(data)
        language_result = await get_language_score(data)
        profilePic_result = await get_profile_score(data)
        banner_result = await get_banner_score(data)
        linkedin_url_result = await get_linkedin_url_score(data)
        recommendation_result = await get_recommendation_score(data)
        activity_result = await get_activity_score(data)
          
        profile_content_format_result = get_profile_content_format(profile_content_result)
        headline_format_result = get_headline_format(headline_result)
        about_format_result = get_about_format(about_result)
        experience_format_result = get_experience_format(experience_result)
        education_format_result = get_education_format(education_result)
        project_format_result = get_project_format(project_result)
        skill_format_result = get_skill_format(skill_result)
        certification_format_result = get_certification_format(certification_result)
        volunteer_format_result = get_volunteer_format(volunteer_result)
        interest_format_result = get_interest_format(interest_result)
        language_format_result = get_language_format(language_result)
        banner_format_result = get_banner_format(banner_result)
        profile_format_result = get_profile_format(profilePic_result)
        linkedin_url_format_result = get_linkedin_url_format(linkedin_url_result)
        recommendation_format_result = get_recommendation_format(recommendation_result)
        activity_format_result = get_activity_format(activity_result)

        
        sections = [profile_content_format_result,headline_format_result, about_format_result, experience_format_result, education_format_result, project_format_result, skill_format_result, certification_format_result, volunteer_format_result, interest_format_result, language_format_result, banner_format_result, profile_format_result, linkedin_url_format_result, recommendation_format_result, activity_format_result]

        scores = [profile_content_result,headline_result, about_result, experience_result, education_result, project_result, skill_result, certification_result, volunteer_result, interest_result, language_result, profilePic_result, banner_result, linkedin_url_result, recommendation_result, activity_result]
        result = 0
        for score in scores:
            result += score.get("score",0)
            print(f"score: {score.get('score',0)}")

        # return {
        #     "profile_content_result" : profile_content_result,  
        #     "profilePic_result" : profile_format_result,
        #     "banner_result" : banner_format_result,
        #     "headline_result": headline_format_result,
        #     "about_result": about_format_result,
        #     "experience_result" : experience_format_result,
        #     "education_result" : education_format_result,
        #     "project_result" : project_format_result,
        #     "skill_result" : skill_format_result,
        #     "certification_result" : certification_format_result,
        #     "volunteer_result" : volunteer_format_result,
        #     "interest_result" : interest_format_result,
        #     "language_result" : language_format_result,
        #     "network_result" : network_result,
        #     "linkedin_url_result" : linkedin_url_format_result
        # }

        return {
            "score" : result,
            "sections" : sections
        }




    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))


@router.get("/user/{user_id}/linkedin-checker/profile")
async def get_linkedin_profile(user_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        # Get user's linkedin profile record
        user_profile_query = select(UserLinkedInProfile).where(UserLinkedInProfile.user_id == user_id)
        user_profile = await db.scalar(user_profile_query)
        
        if not user_profile:
            raise HTTPException(status_code = 404, detail = "Linkedin profile not found")
        
        # Get the linkedin profile data using the profile URL
        linkedin_profile_query = select(LinkedInProfile).where(LinkedInProfile.profile_url == user_profile.linkedin_profile_url)
        linkedin_profile = await db.scalar(linkedin_profile_query)
        
        if not linkedin_profile:
            raise HTTPException(status_code = 404, detail = "Linkedin profile data not found")
        
        # Use profile_report_data if available, otherwise fall back to profile_data
        data_to_return = linkedin_profile.profile_report_data if linkedin_profile.profile_report_data is not None else {}
        return {"status": "success", "data": data_to_return}

    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))


@router.get("/users/{user_id}/profile")
async def get_user_info(user_id: UUID, db: AsyncSession = Depends(get_db)):
    try:
        # Get user's linkedin profile record
        user_profile_query = select(User).where(User.id == user_id)
        user_profile = await db.scalar(user_profile_query)
        
        if not user_profile:
            raise HTTPException(status_code = 404, detail = "User not found")


        return {
            "name": user_profile.name,
            "email": user_profile.email,
            "age": user_profile.age
        }

    except Exception as e:
        raise HTTPException(status_code = 500, detail = str(e))



        

        

