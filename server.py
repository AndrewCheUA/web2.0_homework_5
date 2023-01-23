import asyncio
import logging
import websockets
import names
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK
from pb_request import main_exchange
from aiofile import async_open
from aiopath import AsyncPath
from datetime import datetime


logging.basicConfig(level=logging.INFO)
exchange_log = AsyncPath("exchange.txt")
time_stamp = datetime.now()


class Server:
    clients = set()

    async def register(self, ws: WebSocketServerProtocol):
        ws.name = names.get_full_name()
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects')

    async def unregister(self, ws: WebSocketServerProtocol):
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects')

    async def send_to_clients(self, message: str):
        if self.clients:
            [await client.send(message) for client in self.clients]

    async def ws_handler(self, ws: WebSocketServerProtocol):
        await self.register(ws)
        try:
            await self.distrubute(ws)
        except ConnectionClosedOK:
            pass
        finally:
            await self.unregister(ws)

    async def distrubute(self, ws: WebSocketServerProtocol):
        async for message in ws:
            print(message)
            await self.send_to_clients(f"{ws.name}: {message}")
            if message == "exchange":
                rate = await main_exchange(1)
                await self.send_to_clients(f"Exchange rate for today is {rate}")
                async with async_open(exchange_log, 'a+') as afp:
                    await afp.write(f"{time_stamp} for {ws.name}: \n {rate} \n")
                    
            elif message.startswith('exchange'):
                if len(message.split()) == 2:
                    days = message.split()[1]
                    print(len(message.split()))
                    rate = await main_exchange(days)
                    await self.send_to_clients(f"Exchange rate for {days} days ago till present time: {rate}")
                    async with async_open(exchange_log, 'a+') as afp:
                        await afp.write(f"{time_stamp} for {ws.name}: \n {rate} \n")
                
                elif len(message.split()) == 3:
                    days = message.split()[1]
                    user_currency = message.split()[2]
                    print(len(message.split()), user_currency)
                    rate = await main_exchange(days, user_currency)
                    await self.send_to_clients(f"Exchange rate for {days} days ago till present time: {rate}")
                    async with async_open(exchange_log, 'a+') as afp:
                        await afp.write(f"{time_stamp} for {ws.name}: \n {rate} \n")
                    
                 
                 
async def main():
    server = Server()
    async with websockets.serve(server.ws_handler, 'localhost', 8080):
        await asyncio.Future()  # run forever

if __name__ == '__main__':
    asyncio.run(main())