from fastapi import FastAPI
from logger import get_logger
from api.routers.user import router as user_router
from api.routers.auth import router as auth_router 
from api.routers.ask import router as ask_router
from middleware.middleware import CustomHeaderMiddleware
from middleware.middleware import AskPathMiddleware



logger = get_logger("Main")

app = FastAPI()

app.add_middleware(AskPathMiddleware)   
app.add_middleware(CustomHeaderMiddleware)

logger.info("Middlewares added")


app.include_router(user_router)
app.include_router(auth_router)
app.include_router(ask_router, prefix = "/ask")
logger.info("Routers added")

@app.get("/")
async def root():  # make it async for consistency
    return {"Message": "It's working well"}
