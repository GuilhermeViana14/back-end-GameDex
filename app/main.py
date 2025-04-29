from fastapi import FastAPI
from app.endpoints.user_endpoint import router as user_router
from app.endpoints.api_endpoint import router as api_router

app = FastAPI()

# Registra o endpoint de usuários
app.include_router(user_router, prefix="/api", tags=["users"])
app.include_router(api_router, prefix="/api", tags=["games"])

