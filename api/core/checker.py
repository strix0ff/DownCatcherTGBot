import asyncio
import aioping
import socket

from api.core.database import (
    db_getall
)

from sh.redis import (
    redissession
)

async def service_ping(id: str, address: str, name: str):
    servicestatus = await redissession.get(f'service:{id}:{name}')
    try:
        await aioping.ping(address)
        print(f'Ping OK: {id} | {address} | {name}')
        if servicestatus != 'up':
            await redissession.set(f'service:{id}:{name}', 'up')
    except TimeoutError:
        if servicestatus != 'down':
            await redissession.set(f'service:{id}:{name}', 'down')
        print(f'Service is down {id} | {address} | {name}')
    except socket.gaierror:
        if servicestatus != 'notfound':
            await redissession.set(f'service:{id}:{name}', 'notfound')
        print(f'Service is not found {id} | {address} | {name}')


async def checker():
    while True:
        data = await db_getall()

        if not data:
            await asyncio.sleep(10)
            continue

        tasks = [service_ping(id, service['address'], service['name']) for id, service in data.items()]
        await asyncio.gather(*tasks)
        await asyncio.sleep(10)