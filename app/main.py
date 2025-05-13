from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.endpoints.user_endpoint import router as user_router
from app.endpoints.api_endpoint import router as api_router

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Replace with the frontend's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register the endpoints
app.include_router(user_router, prefix="/api", tags=["users"])
app.include_router(api_router, prefix="/api", tags=["games"])