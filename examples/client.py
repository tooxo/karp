import asyncio

from karp.client import KARPClient
from karp.response import Response

c = KARPClient("0.0.0.0", "9977")


async def run():
    await c.open()
    print("open")
    response: Response = await c.request("test", "hello")
    print(response.text)


asyncio.run(run())
