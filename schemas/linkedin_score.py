from pydantic import BaseModel
from typing import List


class InnerFieldCheck(BaseModel):
    check_type : str
    criteria_meet : bool
    remark : str

class LinkedinHeadlineScoreResponse(BaseModel):
    overall_suggestion: str
    checks: List[InnerFieldCheck]

class LinkedinAboutScoreResponse(BaseModel):
    overall_suggestion: str
    checks: List[InnerFieldCheck]

class ExperienceDescriptionCheck(BaseModel):
    role_clarity: bool
    impact_demonstrated: bool

class LinkedinExperienceDescriptionResponse(BaseModel):
    analysis: ExperienceDescriptionCheck

