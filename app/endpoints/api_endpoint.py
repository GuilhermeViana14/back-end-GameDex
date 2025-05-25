from fastapi import APIRouter, HTTPException, Query
import httpx
from app.components.api_service import fetch_games, fetch_games_by_name, fetch_games_filtered
# -----------------------------------------------------------------------------


router = APIRouter()

# Rota para listar jogos
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

# Rota para buscar jogos por nome  
@router.get("/games/search", summary="Busca jogos por nome")
async def search_games(name: str = Query(..., description="Nome do jogo a ser buscado"), page: int = 1, page_size: int = 10):
    """
    Busca jogos na API RAWG pelo nome.
    """
    try:
        games = await fetch_games_by_name(name=name, page=page, page_size=page_size)
        return games
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/games/filter", summary="Busca jogos com filtros")
async def filter_games(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=40),
    genre: str = Query(None, description="Slug do gênero (ex: action, rpg)"),
    developer: str = Query(None, description="Slug do desenvolvedor (ex: nintendo)"),
    platform: str = Query(None, description="ID da plataforma (ex: 4 para PC)")
):
    """
    Busca jogos na API RAWG usando filtros opcionais: gênero, desenvolvedor e plataforma.
    """
    try:
        games = await fetch_games_filtered(
            page=page,
            page_size=page_size,
            genre=genre,
            developer=developer,
            platform=platform
        )
        return games
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))