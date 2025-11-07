import jwt
import os
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()


url = os.getenv("SUPABASE_JWT")



def get_user_id_from_token(token: str) -> str:
    try:
        decoded = jwt.decode(token, url, algorithms=["HS256"], audience="authenticated")
        return decoded["sub"]
    except jwt.exceptions.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

