from fastapi import APIRouter, HTTPException, Request, Depends
from database import get_db
from supabaseclient import supabase_public 
from models.user import User
from models.query import UserQuery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from logger import get_logger
from services.llm import call_llm
from pydantic import BaseModel
from typing import Any

router = APIRouter()

class LLMResponse(BaseModel):
    """Pydantic model for LLM response"""
    content: Any = None
    answer: Any = None
    
    class Config:
        extra = "allow"  # Allow additional fields

@router.post("/query")  # POST since you receive JSON body
async def ask_me(request: Request, db: AsyncSession = Depends(get_db)):

    auth_head = request.headers.get("Authorization")
    token = auth_head.split(" ")[1]

    res = supabase_public.auth.get_user(token)

    user_id = res.user.id

    data = await request.json()

    id = data.get("id")


    # Query user query count once
    stmt = select(UserQuery).where(UserQuery.id == id)
    result = await db.execute(stmt)
    user_query = result.scalar_one_or_none()

    # If not exists, create new UserQuery with count=1 and commit
    if not user_query:
        user_query = UserQuery(id=id, count=1)
        db.add(user_query)
        await db.commit()
        await db.refresh(user_query)
    else:
        if user_query.count >= 20:
            return {"Message": "Your limit reached max subscribe to our plan for more queries"}

    question = data.get("question")
    if not question:
        raise HTTPException(status_code=400, detail="Question field is required")

    try:
        # Call LLM function with system message and prompt
        system_message = ""  # You can customize this if needed
        parsed_content = await call_llm(
            system_message=system_message,
            prompt=question,
            response_model=LLMResponse
        )

        # Increment count after successful API call
        user_query.count += 1
        your_cuurent_count = user_query.count
        await db.commit()
        await db.refresh(user_query)

        return {
            "Answer": parsed_content,
            "your_current_queries_number": your_cuurent_count,
            "Remaining queries": 20 - your_cuurent_count
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))