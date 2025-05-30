from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
import httpx
from app.components.api_service import fetch_games, fetch_games_by_name, fetch_games_filtered
from app.components.api_service import RAWG_API_KEY
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
    genre: str = Query(None),
    developer: str = Query(None),
    platform: str = Query(None),
    search: str = Query(None),
    best_of_year: bool = Query(False, description="Melhores jogos do ano atual"),
    popular_2024: bool = Query(False, description="Jogos populares de 2024"),
    best_of_all_time: bool = Query(False, description="Melhores jogos de todos os tempos")
):
    """
    Busca jogos usando filtros: gênero, desenvolvedor, plataforma, melhores do ano, populares de 2024 ou melhores de sempre.
    """
    try:
        games = await fetch_games_filtered(
            page=page,
            page_size=page_size,
            genre=genre,
            developer=developer,
            platform=platform,
            search=search,
            best_of_year=best_of_year,
            popular_2024=popular_2024,
            best_of_all_time=best_of_all_time
        )
        return games
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))