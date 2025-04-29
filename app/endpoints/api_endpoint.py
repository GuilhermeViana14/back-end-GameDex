from fastapi import APIRouter, HTTPException, Query
from app.components.api_service import fetch_games

router = APIRouter()

@router.get("/games")
async def list_games(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=40)):
    """
    Lista jogos da API RAWG.
    - `page`: Número da página.
    - `page_size`: Quantidade de jogos por página (máximo: 40).
    """
    try:
        games = await fetch_games(page=page, page_size=page_size)
        return games
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar jogos: {str(e)}")