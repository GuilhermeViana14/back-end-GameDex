import httpx
from fastapi import HTTPException

RAWG_API_BASE_URL = "https://api.rawg.io/api"
RAWG_API_KEY = "17592c02a3204e019ac5a4d4ffd83624" #chave de API

async def fetch_games(page: int = 1, page_size: int = 10):
    """Busca jogos da API RAWG."""
    url = f"{RAWG_API_BASE_URL}/games"
    params = {
        "key": RAWG_API_KEY,
        "page": page,
        "page_size": page_size,
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()

async def fetch_games_by_name(name: str, page: int = 1, page_size: int = 10):
    """Busca jogos da API RAWG por nome."""
    url = f"{RAWG_API_BASE_URL}/games"
    params = {
        "key": RAWG_API_KEY,
        "search": name,
        "page": page,
        "page_size": page_size,
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()


async def fetch_games_filtered(
    page: int = 1,
    page_size: int = 10,
    genre: str = None,
    developer: str = None,
    platform: str = None,
    search: str = None
):
    """Busca jogos da API RAWG com filtros opcionais."""
    url = f"{RAWG_API_BASE_URL}/games"
    params = {
        "key": RAWG_API_KEY,
        "page": page,
        "page_size": page_size,
    }
    if genre:
        params["genres"] = genre
    if developer:
        params["developers"] = developer
    if platform:
        params["platforms"] = platform
    if search:
        params["search"] = search

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    
def fetch_game_from_rawg(rawg_id: int):
    """
    Busca detalhes de um jogo específico na API RAWG.io.
    """
    url = f"https://api.rawg.io/api/games/{rawg_id}?key={RAWG_API_KEY}"
    response = httpx.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            "name": data["name"],
            "rawg_id": data["id"],
            "background_img": data.get("background_image"),
            "platforms": ", ".join([platform["platform"]["name"] for platform in data["platforms"]]),
            "release_date": data.get("released")  # Obtendo a data de lançamento
        }
    else:
        raise HTTPException(status_code=response.status_code, detail="Erro ao buscar jogo na RAWG.io")

