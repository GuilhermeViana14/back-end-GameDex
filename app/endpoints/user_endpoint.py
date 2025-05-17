from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models.User import User
from app.components.password_utils import hash_password, verify_password
from app.database import get_db
from pydantic import BaseModel, Field
from fastapi import status
from app.models.Game import Game

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

class UserLogin(BaseModel):
    email: str
    password: str

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
    
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    # Busca o usuário pelo e-mail
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    # Verifica a senha
    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    # Retorna uma mensagem de sucesso (ou um token, caso implemente autenticação JWT no futuro)
    return {"message": "Login successful", "user": {"email": db_user.email, "first_name": db_user.first_name}}

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

@router.delete("/users/{user_id}/games/{game_id}")
def remove_game_from_user(user_id: int, game_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Jogo não encontrado")

    # Remove o jogo da lista do usuário, se estiver associado
    if game in user.games:
        user.games.remove(game)
        db.commit()
        return {"message": "Jogo removido com sucesso", "user": user.email, "game": game.name}
    else:
        raise HTTPException(status_code=404, detail="Este jogo não está associado a este usuário")
