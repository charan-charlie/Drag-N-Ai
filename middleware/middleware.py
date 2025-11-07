from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException
from supabaseclient import supabase_public
import time
from logger import get_logger

logger = get_logger("MiddleWare")

class CustomHeaderMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()
        
        logger.info("Middleware triggered for %s %s", request.method, request.url)
        
        response = await call_next(request)
        
        process_time = time.perf_counter() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.4f}s"
        
        return response
    


class AskPathMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        target_paths = ["/ask"]

        # Check if the path starts with any target path
        if not any(request.url.path.startswith(path) for path in target_paths):
            response =  await call_next(request)
            return response
        
        auth_head = request.headers.get("Authorization")
        if not auth_head or not auth_head.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid token")
        token = auth_head.split(" ")[1]

        res = supabase_public.auth.get_user(token)
        if not res.user:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        data = await request.json()
        id = data.get("id")

        print(id)
        if not id:
            raise HTTPException(status_code=400, detail="id field is required")
        
        if id != res.user.id:
            raise HTTPException(status_code=403, detail="Not authorized to access this user")
        
        response = await call_next(request)
        return response
            



        
