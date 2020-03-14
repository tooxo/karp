"""
KARP - Server
"""

import asyncio
from typing import Optional
from concurrent.futures import ThreadPoolExecutor
from karp.request import Request
from karp.response import Response


class InvalidRouteNameException(Exception):
    """
    Raised if route does not exist
    """
    pass


class KARPServer:
    """
    KARPServer
    """
    def __init__(self, hostname: str, port: str):
        self.routes: dict = {}
        self.hostname = hostname
        self.port = port

        self.server: Optional[asyncio.AbstractServer] = None

        self.stopped = False

        self.executor = ThreadPoolExecutor(max_workers=5)

    async def start(self) -> None:
        """
        Creates a new KARP Server and starts it
        :return: Future
        """
        self.server = await asyncio.start_server(
            self._new_connection, host=self.hostname, port=self.port
        )
        return await self.server.serve_forever()

    async def _create_response(self, request: bytes) -> bytes:
        if not request:
            return b""
        req: Request = Request.parse(request)
        response_data = await asyncio.get_event_loop().run_in_executor(
            self.executor, self.routes[req.route], req
        )
        res = Response.create(req.request_id, response_data)
        return res.to_bytes()

    async def _new_connection(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        while not self.stopped:
            try:
                requests = await reader.read(100000)
            except BrokenPipeError:
                break
            if not requests:
                break
            print("lulu")

            for request in requests.decode().split("\n"):
                response: bytes = await self._create_response(
                    bytes(request, "UTF-8")
                )
                if response:
                    writer.write(response)
                    await writer.drain()

    def add_route(self, func, route_name=None) -> None:
        """
        Adds a route, which returns the func provided
        :param route_name: route name
        :param func: function to call on route
        :return:
        """
        if not route_name:
            raise InvalidRouteNameException("No route name provided.")
        self.routes[route_name] = func
        print(f"Route '{route_name}' registered.")

    def __del__(self) -> None:
        self.stopped = True
        self.server.close()
