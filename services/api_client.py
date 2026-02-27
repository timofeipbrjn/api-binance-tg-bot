import aiohttp

class CurrencyApiClient:
    def __init__(self, url:str) -> None:
        self.url = url

    async def get_data(self, symbol: str):
        params = {"symbol": symbol}

        async with aiohttp.ClientSession() as session:
            async with session.get(self.url, params=params) as response:
                return await response.json()
