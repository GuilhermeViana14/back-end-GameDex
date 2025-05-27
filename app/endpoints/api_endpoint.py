from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
import httpx
from app.components.api_service import fetch_games, fetch_games_by_name, fetch_games_filtered
# -----------------------------------------------------------------------------
RAWG_API_KEY = "17592c02a3204e019ac5a4d4ffd83624"

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
    platform: str = Query(None, description="ID da plataforma (ex: 4 para PC)"),
    best_of_year: bool = Query(False, description="Se verdadeiro, busca os melhores jogos do ano atual"),
):
    """
    Busca jogos na API RAWG usando filtros opcionais: gênero, desenvolvedor e plataforma.
    Quando `best_of_year` é verdadeiro, filtra os jogos do ano atual ordenados por nota.
    """
    try:
        # Prepare filter parameters
        params = {
            "page": page,
            "page_size": page_size,
            "key": RAWG_API_KEY,
        }

        if genre:
            params["genres"] = genre
        if developer:
            params["developers"] = developer
        if platform:
            params["platforms"] = platform
        if best_of_year:
            current_year = datetime.now().year
            params["dates"] = f"{current_year}-01-01,{current_year}-12-31"
            params["ordering"] = "-rating"

        async with httpx.AsyncClient() as client:
            response = await client.get("https://api.rawg.io/api/games", params=params)
            response.raise_for_status()
            return response.json()
        return games
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))