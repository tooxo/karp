import asyncio

from karp.client import KARPClient
from karp.response import Response

c = KARPClient("0.0.0.0", "9977")


async def run():
    await c.open()
    response: Response = await c.request("test", "hello")
    print(response.text)

    await asyncio.sleep(1)
    response: Response = await c.request("error", "this is not important")
    print(str(response))


asyncio.run(run())
