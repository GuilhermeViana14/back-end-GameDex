from fastapi import FastAPI
from app.endpoints.user_endpoint import router as user_router

app = FastAPI()

# Registra o endpoint de usuários
app.include_router(user_router, prefix="/api", tags=["users"])


