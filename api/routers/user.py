from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from models.user import User
from schemas.user import UserOut
from schemas.user import UserIn
from database import get_db
from utils.getuser import get_user_id_from_token
from supabaseclient import supabase, get_user_client, supabase_public
from logger import get_logger

logger = get_logger("user router")



router = APIRouter()

# @router.post("/add_user", response_model=UserOut)
# async def add_user(name: str, email: str, age: int, db: AsyncSession = Depends(get_db)):
#     user = User(name=name, email=email, age=age)
#     db.add(user)
#     await db.commit()
#     await db.refresh(user)
#     return user


@router.put("/update_user", response_model=UserOut)
async def update_user(
    request: Request,
    id: str,
    data: UserIn,
    db: AsyncSession = Depends(get_db)
):
    logger.info("Enter into update user end point")
    """
    Update the logged-in user's profile in both Supabase Auth and local DB.
    - Access token from Authorization header
    - Refresh token from JSON body
    """

    # 1️ Extract access token
    auth_head = request.headers.get("Authorization")
    if not auth_head or not auth_head.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    
    access_token = auth_head.split(" ")[1]

    # 2️ Extract refresh token from request body
    if not data.refresh_token:
        raise HTTPException(status_code=400, detail="Refresh token is required")
    refresh_token = data.refresh_token

    logger.info("User has both access token and refresh token")

    # 3️ Create authenticated Supabase client
    supabase_user = get_user_client(access_token, refresh_token)
    logger.info("Got the client object for the user")


    # 4️ Verify logged-in user
    try:
        user_info = supabase_user.auth.get_user()
        if not user_info.user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        user_id = user_info.user.id
        logger.info("User has been verified and got the user id")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")

    # 5️ Only allow self-update
    print(id)
    print(user_id)
    if id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this user")

    # 6️ Prepare Supabase Auth update data
    update_data = {}
    if data.password:
        update_data["password"] = data.password
    if data.email:
        update_data["email"] = data.email

    # 7️ Update in Supabase Auth
    try:
        if update_data:
            res = supabase_user.auth.update_user(update_data)
            if not res.user:
                raise HTTPException(status_code=400, detail="Failed to update Supabase user")
            logger.info("User has been been updated in supabase")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Supabase update error: {str(e)}")

    # 8️ Update local DB
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if data.name:
        user.name = data.name
    if data.email:
        user.email = data.email
    if data.age:
        user.age = data.age

    logger.info("User has been been updated in db")


    await db.commit()
    await db.refresh(user)

    logger.info("User has been been refreshed")

    return user



@router.get("/all_users", response_model=list[UserOut])
async def get_users(db: AsyncSession = Depends(get_db)):
    logger.info("Enter into get users end point")
    query = select(User)
    result = await db.execute(query)
    users = result.scalars().all()

    if not users:
        raise HTTPException(status_code=404, detail="No users found")
    logger.info("Users has been been fetched")
    return users


@router.get("/id", response_model=UserOut)
async def get_user_by_id(
    id: str, 
    request: Request, 
    db: AsyncSession = Depends(get_db)
):
    # Extract and validate token
    auth_head = request.headers.get("Authorization")
    if not auth_head or not auth_head.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    token = auth_head.split(" ")[1]


    #user_id = get_user_id_from_token(access_token) it will use jwt decoder or else we can use in built function of supabase but it is bit slow cause we are making api request
    #we can use supabase which will use service role key and also we can use supabase_public which will user anon key
    
    res = supabase_public.auth.get_user(token) 
    if not res.user:
        raise HTTPException(status_code=401, detail="Invalid token")
    user_id = res.user.id
    
    print(id) #ea4636af-e326-4f26-a556-631016ece2df
    print(user_id) 
    

    if id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this user")
    
    # Fetch user from database
    stmt = select(User).where(User.id == id)
    
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found with the id")
    
    return user



@router.delete("/delete_users")
async def delete_all_users(db: AsyncSession = Depends(get_db)):
    try:
        # Step 1: Fetch all users from your database (including Supabase auth IDs)
        users = await db.execute(select(User))  # Adjust query if needed
        user_list = users.scalars().all()

        # Step 2: Delete users from Supabase Auth
        for user in user_list:
            # Supabase Auth requires admin privileges (use service role key!)
            supabase.auth.admin.delete_user(user.id)  # Replace `supabase_id` with your column name

        # Step 3: Delete users from your database
        await db.execute(delete(User))
        await db.commit()

        return {"message": "All users deleted successfully."}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    
@router.delete("/delete_user")
async def delete_user(id: str, request: Request, db: AsyncSession = Depends(get_db)):
    # Extract bearer token
    auth_head = request.headers.get("Authorization")
    if not auth_head or not auth_head.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    token = auth_head.split(" ")[1]
    
    # Verify the token using anon key client
    res = supabase_public.auth.get_user(token)
    if not res.user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_id = res.user.id

    print(id)
    print(user_id)
    # Ensure the user can only delete themselves
    if id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this user")
    
    # Delete from your DB
    stmt = delete(User).where(User.id == id)
    await db.execute(stmt)
    await db.commit()
    print("deleted from db")
    # Delete from Supabase Auth (requires service role key)
    try:
        print("Before deletion from supabase")
        supabase.auth.admin.delete_user(id)  # supabase must be service-role client
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete user from Supabase: {str(e)}")

    return {"message": "User deleted successfully"}    

