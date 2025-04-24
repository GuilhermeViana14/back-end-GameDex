from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models.User import User
from app.components.password_utils import hash_password
from app.database import get_db
from pydantic import BaseModel, Field

router = APIRouter()

class UserCreate(BaseModel):
    first_name: str = Field(alias="Name")
    email: str
    password: str

# Modelo de resposta (sem o campo password)
class UserResponse(BaseModel):
    first_name: str
    email: str

    class Config:
        from_attributes = True  # Substitui `orm_mode` no Pydantic v2

@router.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        # Verifica se o e-mail já está cadastrado
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Hash da senha antes de salvar
        hashed_password = hash_password(user.password)
        db_user = User(first_name=user.first_name, email=user.email, password=hashed_password)

        # Salva o usuário no banco de dados
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        return db_user
    except Exception as e:
        # Log detalhado do erro
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    
    
    
@router.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    try:
        result = db.execute("SELECT 1").fetchall()
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "detail": str(e)}