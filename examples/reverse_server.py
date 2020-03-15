"""

"""
import asyncio
import logging

from karp.request import Request
from karp.server import KARPServer

k = KARPServer("0.0.0.0", "9977")

logging.getLogger("karp").setLevel(logging.DEBUG)


async def send_request():
    s = await k.clients[list(k.clients.keys())[0]].request("test", "test", True)
    return s


@k.add_route(route="echo")
async def back(request: Request):
    r = await send_request()
    return request.text


asyncio.run(k.start())
