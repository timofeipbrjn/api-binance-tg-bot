import aiohttp

class CurrencyApiClient:
    def __init__(self, url:str, session:aiohttp.ClientSession) -> None:
        self.session = session
        self.url = url

    async def get_data(self, symbol: str):
        params = {"symbol": symbol}

        async with self.session.get(self.url, params=params) as response:
            response.raise_for_status()
            data = await response.json()

        r_price = data.get('price')
        return str(r_price).rstrip("0").rstrip(".")
