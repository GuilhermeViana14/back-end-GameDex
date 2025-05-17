# FastAPI e dependências
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError

# SQLAlchemy
from sqlalchemy.orm import Session

# Models
from app.models.User import User
from app.models.Game import Game, UserGame

# Schemas
from app.schemas.user import UserCreate, UserResponse, UserLogin
from app.schemas.game import GameCreate, GameUpdate

# Utils e componentes
from app.components.password_utils import hash_password, verify_password
from app.components.jwt_utils import create_access_token, decode_access_token
from app.database import get_db
from app.components.jwt_utils import get_current_user

# -----------------------------------------------------------------------------


router = APIRouter()



#cadastro do usuario
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
    

#testar o banco de dados
@router.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    try:
        result = db.execute("SELECT 1").fetchall()
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


#login do usuario  
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    access_token = create_access_token(data={"sub": db_user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"email": db_user.email, "first_name": db_user.first_name, "id": db_user.id,}
    }


@router.post("/users/{user_id}/games")
def add_game_to_user(user_id: int, game_data: GameCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Verifica se o jogo já existe no banco
    game = db.query(Game).filter(Game.rawg_id == game_data.rawg_id).first()
    if not game:
        game = Game(
            name=game_data.name,
            rawg_id=game_data.rawg_id,
            background_img=game_data.background_img,
            platforms=game_data.platforms
        )
        db.add(game)
        db.commit()
        db.refresh(game)

    # Verifica se já existe associação UserGame
    user_game = db.query(UserGame).filter_by(user_id=user.id, game_id=game.id).first()
    if not user_game:
        user_game = UserGame(
            user_id=user.id,
            game_id=game.id,
            comment=game_data.comment,
            rating=game_data.rating,
            progress=game_data.progress
        )
        db.add(user_game)
        db.commit()
        db.refresh(user_game)
    else:
        # Atualiza dados se já existir
        user_game.comment = game_data.comment
        user_game.rating = game_data.rating
        user_game.progress = game_data.progress
        db.commit()
        db.refresh(user_game)

    return {
        "message": "Jogo adicionado/atualizado com sucesso",
        "user": user.email,
        "game": game.name,
        "background_img": game.background_img,
        "comment": user_game.comment,
        "rating": user_game.rating,
        "progress": user_game.progress,
        "platforms": game.platforms,
    }
@router.put("/users/{user_id}/games/{game_id}")
def update_user_game(user_id: int, game_id: int, game_update: GameUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    user_game = db.query(UserGame).filter_by(user_id=user_id, game_id=game_id).first()
    if not user_game:
        raise HTTPException(status_code=404, detail="Jogo não encontrado para este usuário")
    
    # Atualiza os campos fornecidos
    if game_update.comment is not None:
        user_game.comment = game_update.comment
    if game_update.rating is not None:
        user_game.rating = game_update.rating
    if game_update.progress is not None:
        user_game.progress = game_update.progress

    db.commit()
    db.refresh(user_game)

    return {
        "message": "Informações do jogo atualizadas com sucesso",
        "game_id": game_id,
        "user_id": user_id,
        "comment": user_game.comment,
        "rating": user_game.rating,
        "progress": user_game.progress
    }


@router.get("/users/{user_id}/games")
def list_user_games(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    # Retorna a lista de jogos associados ao usuário, com dados personalizados
    games = []
    for user_game in user.user_games:
        game = user_game.game
        games.append({
            "id": game.id,
            "name": game.name,
            "rawg_id": game.rawg_id,
            "background_img": game.background_img,
            "platforms": game.platforms,
            "comment": user_game.comment,
            "rating": user_game.rating,
            "progress": user_game.progress
        })
    return {"user": user.email, "games": games}


# Exemplo de rota protegida
@router.get("/me")
def read_users_me(current_user: str = Depends(get_current_user)):
    return {"email": current_user}
