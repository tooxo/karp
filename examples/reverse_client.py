"""
This is an example, which uses both side connections. The server sends a request to the client,
and the client answers it.
"""
import asyncio

from karp.client import KARPClient
from karp.request import Request

c = KARPClient("0.0.0.0", "9977")


@c.add_route(route="test")
async def test(request: Request):
    return request.text


async def run():
    await c.open()
    await c.request("echo", "this is not important")


asyncio.run(run())
