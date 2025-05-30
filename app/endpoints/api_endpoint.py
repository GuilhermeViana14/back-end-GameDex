from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
import httpx
from app.components.api_service import fetch_games, fetch_games_by_name, fetch_games_filtered

RAWG_API_KEY = "17592c02a3204e019ac5a4d4ffd83624"

router = APIRouter()

# Rota para listar jogos
@router.get("/games")
async def list_games(page: int = Query(1, ge=1), page_size: int = Query(10, ge=1, le=40)):
    try:
        games = await fetch_games(page=page, page_size=page_size)
        return games
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar jogos: {str(e)}")

# Rota para buscar jogos por nome  
@router.get("/games/search", summary="Busca jogos por nome")
async def search_games(name: str = Query(...), page: int = 1, page_size: int = 10):
    try:
        games = await fetch_games_by_name(name=name, page=page, page_size=page_size)
        return games
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Rota com filtros
@router.get("/games/filter", summary="Busca jogos com filtros")
async def filter_games(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=40),
    genre: str = Query(None),
    developer: str = Query(None),
    platform: str = Query(None),
    best_of_year: bool = Query(False, description="Melhores jogos do ano atual"),
    popular_2024: bool = Query(False, description="Jogos populares de 2024"),
    best_of_all_time: bool = Query(False, description="Melhores jogos de todos os tempos")
):
    """
    Busca jogos usando filtros: gênero, desenvolvedor, plataforma, melhores do ano, populares de 2024 ou mehores de sempre.
    """
    try:
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
            params["ordering"] = "-metacritic"
        elif popular_2024:
            params["dates"] = "2024-01-01,2024-12-31"
            params["ordering"] = "-added"
        elif best_of_all_time:
            params["ordering"] = "-metacritic"    

        async with httpx.AsyncClient() as client:
            response = await client.get("https://api.rawg.io/api/games", params=params)
            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))