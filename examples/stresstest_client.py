import asyncio
import time

from karp.client import KARPClient
from karp.response import Response

c = KARPClient("0.0.0.0", "9977")


async def run():
    await c.open()
    t = time.time()
    requests = 100000
    for x in range(requests):
        response: Response = await c.request("echo", str(x))
        if response.text != str(x):
            raise Exception("oh shit")

    end = time.time() - t

    print(
        f"{requests} Requests done in {end}s. No Errors occurred. The average request was finished in {end / requests}s"
    )


asyncio.run(run())


# This results in:

# 100000 Requests done in 77.4501371383667s.
# No Errors occurred.
# The average request was finished in 0.000774501371383667s

# Works perfectly.
