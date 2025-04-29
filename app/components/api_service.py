import httpx

RAWG_API_BASE_URL = "https://api.rawg.io/api"
RAWG_API_KEY = "17592c02a3204e019ac5a4d4ffd83624"  # Substitua pela sua chave de API da RAWG

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