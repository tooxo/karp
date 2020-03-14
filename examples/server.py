import asyncio
from karp.server import KARPServer
from karp.response import Response

k = KARPServer("0.0.0.0", "9977")


def test(response: Response):
    return response.request_id


k.add_route(test, "test")


asyncio.run(k.start())
