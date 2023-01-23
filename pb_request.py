import platform
import aiohttp
import asyncio
from datetime import datetime, timedelta


def link_generator(number):
    if 0 < number < 11:
        date = datetime.today().date()
        url_list = []
        for day in range(number):
            x_day = date - timedelta(day)
            url_list.append(f'https://api.privatbank.ua/p24api/exchange_rates?json&date={x_day.strftime("%d.%m.%Y")}')
        return url_list
    else:
        return "Invalid number"
    
    
async def currency_request(url):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status == 200:
                    result = await response.json()
                    return result
                else:
                    print(f"Error status: {response.status} for {url}")
        except aiohttp.ClientConnectorError as err:
            print(f'Connection error: {url}', str(err))
            

async def main_exchange(days, user_currency: str = None):
    currency_list = ['USD', 'EUR']
    try:
        url_list = link_generator(int(days))
    except Exception as ex:
        return f"Invalid input. Error: {ex}"
    task_list = []
    for url in url_list:
        task = asyncio.create_task(currency_request(url))
        task_list.append(task)
    result = await asyncio.gather(*task_list, return_exceptions=True)
    final_dict = []
    try:
        for i in result:
            if user_currency != None:
                currency_list.append(user_currency.upper())
            currency = {}
            for item in i.get('exchangeRate'):
                if item['currency'] in currency_list:
                    usd_dict = {"sale": item['saleRateNB'], 'purchase': item['purchaseRateNB']}
                    currency[item['currency']] = usd_dict
            currency_dict = {i.get('date'):currency}
            final_dict.append(currency_dict)
        return final_dict
    except Exception as ex:
        return f"Invalid input. Error: {ex}"


if __name__ == "__main__":
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    message = input ("Please enter number of days and adiitional currency(if applicable): ")
    try:
        days = message.split()[0]
        if len(message.split()) == 1:
            result = asyncio.run(main_exchange(days))
            print(result)
        elif len(message.split()) == 2:
            user_currency = message.split()[1]
            result = asyncio.run(main_exchange(days, user_currency))
            print(result)
    except Exception as ex:
        print(f"Invalid input. Error: {ex}")
