import asyncio
import logging
import time

from karp.request import Request
from karp.server import KARPServer

k = KARPServer("0.0.0.0", "9977")

logging.getLogger("karp").setLevel(logging.INFO)


@k.add_route(route="test")
def error(request: Request):
    return "this is america"


@k.add_route(route="echo")
def echo(request: Request):

    return request.text


try:
    asyncio.run(k.start())
except KeyboardInterrupt:
    del k
