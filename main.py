import aiohttp
import asyncio
import datetime
import sys

class APIClient:
    BASE_URL = "https://api.privatbank.ua/p24api/exchange_rates"

    async def get_exchange_rate(self, date):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.BASE_URL}?json&date={date}") as response:
                if response.status != 200:
                    raise ValueError(f"Failed to fetch data for date {date}.")
                return await response.json()

class CurrencyConverter:
    @staticmethod
    def convert_data(data_list):
        converted_data = []
        for data in data_list:
            if "exchangeRate" in data:
                date = data.get("date", "N/A")
                rates = {}
                for item in data["exchangeRate"]:
                    currency = item["currency"]
                    if currency in ["USD", "EUR"]:
                        rates[currency] = {
                            "sale": item.get("saleRate", "N/A"),
                            "purchase": item.get("purchaseRate", "N/A")
                        }
                if rates:
                    converted_data.append({date: rates})
        return converted_data

class CurrencyDataProvider:
    def __init__(self, api_client):
        self.api_client = api_client

    async def get_currency_data(self, days=10):
        if days > 10:
            days = 10
        today = datetime.date.today()
        dates = [today - datetime.timedelta(days=i) for i in range(days)]
        dates = [date for date in dates if date <= today]  # Виключаємо майбутні та дати поза обмеженням
        data = await asyncio.gather(*[self.api_client.get_exchange_rate(date.strftime("%d.%m.%Y")) for date in dates])
        return CurrencyConverter.convert_data(data)


async def main():
    if len(sys.argv) < 2:
        print("Usage: py main.py <number_of_days>")
        return

    try:
        days = int(sys.argv[1])
        if days <= 0 or days > 10:
            raise ValueError("Number of days must be between 1 and 10.")
    except ValueError as e:
        print("Error:", e)
        return

    api_client = APIClient()
    data_provider = CurrencyDataProvider(api_client)
    currency_data = await data_provider.get_currency_data(days)

    print(currency_data)

if __name__ == "__main__":
    asyncio.run(main())
