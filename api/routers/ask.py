from fastapi import APIRouter, HTTPException, Request, Depends
from database import get_db
from supabaseclient import supabase_public 
from models.user import User
from models.query import UserQuery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from logger import get_logger

import httpx
import json

router = APIRouter()

api_key = "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"
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

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [{"role": "user", "content": question}],
        "temperature": 0.2,
        "max_tokens": 256
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            response_data = response.json()

            content = response_data['choices'][0]['message']['content'].strip()

            try:
                parsed_content = json.loads(content)
            except json.JSONDecodeError:
                parsed_content = content

            # Increment count after successful API call
            user_query.count += 1
            your_cuurent_count  = user_query.count
            await db.commit()
            await db.refresh(user_query)

            return {"Answer": parsed_content, "your_current_queries_number": your_cuurent_count, "Remaining queries" : 20 - your_cuurent_count}

        except httpx.HTTPStatusError as http_err:
            raise HTTPException(status_code=response.status_code, detail=f"HTTP error: {http_err}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))