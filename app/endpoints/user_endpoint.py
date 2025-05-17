from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.models.User import User
from app.components.password_utils import hash_password, verify_password
from app.database import get_db
from pydantic import BaseModel, Field
from app.components.jwt_utils import create_access_token, decode_access_token
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from fastapi import status
from app.models.Game import Game


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

class UserCreate(BaseModel):
    first_name: str
    email: str
    password: str

class UserResponse(BaseModel):
    first_name: str
    email: str

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: str
    password: str

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = decode_access_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/cadastro", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        hashed_password = hash_password(user.password)
        db_user = User(first_name=user.first_name, email=user.email, password=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    
@router.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    try:
        result = db.execute("SELECT 1").fetchall()
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
    
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    access_token = create_access_token(data={"sub": db_user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"email": db_user.email, "first_name": db_user.first_name}
    }


class GameCreate(BaseModel):
    name: str
    rawg_id: int

@router.post("/users/{user_id}/games")
def add_game_to_user(user_id: int, game_data: GameCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Verifica se o jogo já existe no banco
    game = db.query(Game).filter(Game.rawg_id == game_data.rawg_id).first()
    if not game:
        game = Game(name=game_data.name, rawg_id=game_data.rawg_id)
        db.add(game)
        db.commit()
        db.refresh(game)

    # Adiciona o jogo à lista do usuário, se ainda não estiver associado
    if game not in user.games:
        user.games.append(game)
        db.commit()
        db.refresh(user)

    return {"message": "Jogo adicionado com sucesso", "user": user.email, "game": game.name}
=======
# Exemplo de rota protegida
@router.get("/me")
def read_users_me(current_user: str = Depends(get_current_user)):
    return {"email": current_user}
