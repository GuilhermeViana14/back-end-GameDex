from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.endpoints.user_endpoint import router as user_router
from app.endpoints.api_endpoint import router as api_router

app = FastAPI()


# Register the endpoints
app.include_router(user_router, prefix="/api", tags=["cadastro"])


# Configuração do CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Permitir apenas o front-end
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos os métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permitir todos os cabeçalhos
)

# Registra os endpoints
app.include_router(user_router, prefix="/api", tags=["users"])
app.include_router(api_router, prefix="/api", tags=["games"])