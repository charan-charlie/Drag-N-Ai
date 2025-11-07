from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user import SignUpData
from schemas.user import LoginData
from models.user import User
from sqlalchemy import select
from database import get_db
from pydantic import BaseModel,EmailStr
from supabaseclient import supabase
from logger import get_logger

logger = get_logger("auth router")

# we can use for supabase_public for client services like self registration, so we can also with anon key 



router = APIRouter()


@router.post("/signup")
async def signup(data: SignUpData, db: AsyncSession = Depends(get_db)):
    logger.info("Enter into signup end point")
    # Check if user already exists
    query = select(User).where(User.email == data.email)
    result = await db.execute(query)
    existing_user = result.scalar_one_or_none()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists, try logging in directly")

    try:
        # Create user in Supabase with metadata
        res = supabase.auth.sign_up({
            "email": data.email,
            "password": data.password
            })

        if res.user is None:
            raise HTTPException(status_code=400, detail="Failed to create user in Supabase")

        user = User(
            id=res.user.id,
            name=data.name,
            email=data.email,
            age=data.age
        )
        db.add(user)
        
        await db.commit()
        logger.info("User has been been added")

        await db.refresh(user)
        logger.info("User has been been refreshed")

        return {"message": "User created successfully", "user": user}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


    
@router.post("/login")
async def login(data: LoginData, db: AsyncSession = Depends(get_db)):
    logger.info("Enter into login end point")
    # Check if user exists
    query = select(User).where(User.email == data.email)
    result = await db.execute(query)
    result = result.scalar_one_or_none()
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        # Authenticate user call supabase auth sign_in API
        res = supabase.auth.sign_in_with_password(
            {
                "email": data.email,
                "password": data.password
            }
        )
        logger.info("User has been been authenticated")

        if res.session is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        #return access token from the session

        access_token = res.session.access_token
        refresh_token = res.session.refresh_token

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "message": "User logged in successfully",
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


    
    
        



