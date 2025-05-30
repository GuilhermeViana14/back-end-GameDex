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
from app.components.password_utils import hash_password, verify_password, validate_password_strength
from app.components.jwt_utils import create_access_token, decode_access_token
from app.database import get_db
from app.components.jwt_utils import get_current_user
from app.components.email_service import send_reset_password_email, send_confirmation_email
from app.components.api_service import fetch_game_from_rawg
from datetime import timedelta

# -----------------------------------------------------------------------------


router = APIRouter()

@router.post("/cadastro", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        # Gerar hash da senha antes de salvar
        hashed_password = hash_password(user.password)
        db_user = User(
            first_name=user.first_name,
            email=user.email,
            password=hashed_password,
            is_active=False
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

        # Gera token de confirmação
        confirmation_token = create_access_token(data={"sub": db_user.email}, expires_delta=timedelta(hours=24))
        send_confirmation_email(db_user.email, confirmation_token)

        return db_user
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")
    
#confirmação de cadastro
@router.get("/confirm-email")
def confirm_email(token: str, db: Session = Depends(get_db)):
    try:
        payload = decode_access_token(token)
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=400, detail="Token inválido ou expirado")
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        if user.is_active:
            return {"message": "Conta já confirmada"}
        user.is_active = True
        db.commit()
        return {"message": "Cadastro confirmado com sucesso"}
    except JWTError:
        raise HTTPException(status_code=400, detail="Token inválido ou expirado")
    
# Testar o banco de dados
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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email ou senha inválidos")
    if not db_user.is_active:
        raise HTTPException(status_code=403, detail="Confirme seu cadastro pelo e-mail antes de fazer login.")
    access_token = create_access_token(data={"sub": db_user.email})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {"email": db_user.email, "first_name": db_user.first_name, "id": db_user.id,}
    }

# Adicionar jogo
@router.post("/users/{user_id}/games")
def add_game_to_user(user_id: int, game_data: GameCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Verifica se o jogo já existe no banco
    game = db.query(Game).filter(Game.rawg_id == game_data.rawg_id).first()
    if not game:
        # Busca os dados do jogo na RAWG.io
        fetched_game = fetch_game_from_rawg(game_data.rawg_id)
        game = Game(
            name=fetched_game["name"],
            rawg_id=fetched_game["rawg_id"],
            background_img=fetched_game["background_img"],
            platforms=fetched_game["platforms"],
            release_date=fetched_game["release_date"]  # Salva a data de lançamento
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

    return {
        "message": "Jogo adicionado/atualizado com sucesso",
        "user": user.email,
        "game": game.name,
        "release_date": game.release_date,
        "background_img": game.background_img,
        "comment": user_game.comment,
        "rating": user_game.rating,
        "progress": user_game.progress,
        "platforms": game.platforms,
    }

# Editar jogos adicionados
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

# Listar jogos do usuário
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
            "release_date": game.release_date,
            "comment": user_game.comment,
            "rating": user_game.rating,
            "progress": user_game.progress
        })
    return {"user": user.email, "games": games}

# Remover jogo do usuário
@router.delete("/users/{user_id}/games/{game_id}")
def remove_game_from_user(user_id: int, game_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Jogo não encontrado")

    # Remove a associação UserGame
    user_game = db.query(UserGame).filter_by(user_id=user_id, game_id=game_id).first()
    if not user_game:
        raise HTTPException(status_code=404, detail="Este jogo não está associado a este usuário")

    db.delete(user_game)
    db.commit()

    # Verifica se mais alguém tem esse jogo
    remaining = db.query(UserGame).filter_by(game_id=game_id).first()
    if not remaining:
        db.delete(game)
        db.commit()

    return {"message": "Jogo removido com sucesso", "user": user.email, "game": game.name}

# Exemplo de rota protegida
@router.get("/me")
def read_users_me(current_user: str = Depends(get_current_user)):
    return {"email": current_user}

# Esqueci minha senha
@router.post("/forgot-password", operation_id="forgot_password")
def forgot_password(email: str, db: Session = Depends(get_db)):
    from email_validator import validate_email, EmailNotValidError

    # Valida o formato do e-mail
    try:
        validate_email(email)
    except EmailNotValidError:
        raise HTTPException(status_code=400, detail="E-mail inválido")

    # Verifica se o usuário existe
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Gera o token de redefinição de senha
    reset_token = create_access_token(data={"sub": user.email}, expires_delta=timedelta(minutes=30))

    # Tenta enviar o e-mail
    try:
        send_reset_password_email(email, reset_token)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao enviar e-mail: {str(e)}")

    # Retorna uma mensagem de sucesso
    return {"message": "E-mail de redefinição de senha enviado com sucesso"}

# Trocar senha
@router.post("/reset-password", operation_id="reset_password")
def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    from app.components.jwt_utils import decode_access_token
    from app.components.password_utils import hash_password, validate_password_strength

    # Decodifica o token para obter o e-mail do usuário
    try:
        payload = decode_access_token(token)
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=400, detail="Token inválido ou expirado")
    except JWTError:
        raise HTTPException(status_code=400, detail="Token inválido ou expirado")

    # Verifica se o usuário existe
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    # Valida a força da nova senha
    if not validate_password_strength(new_password):
        raise HTTPException(
            status_code=400,
            detail="A senha deve ter pelo menos 8 caracteres, uma letra maiúscula e um caractere especial."
        )

    # Atualiza a senha do usuário
    hashed_password = hash_password(new_password)
    user.password = hashed_password
    db.commit()

    return {"message": "Senha alterada com sucesso"}