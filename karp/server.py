"""
KARP - Server
"""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Optional

from karp.request import Request
from karp.response import Response

logging.basicConfig(level=logging.WARNING)


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

        self.logger = logging.getLogger("karp")
        self.logger.setLevel(logging.DEBUG)

    async def start(self) -> None:
        """
        Creates a new KARP Server and starts it
        :return: Future
        """
        self.server = await asyncio.start_server(
            self._new_connection, host=self.hostname, port=self.port
        )
        self.logger.info(f"KARPServer started on {self.hostname}:{self.port}")
        return await self.server.serve_forever()

    async def _create_response(self, request: bytes) -> bytes:
        if not request:
            return b""
        req: Request = Request.parse(request)
        try:
            response_data = await asyncio.get_event_loop().run_in_executor(
                self.executor, self.routes[req.route], req
            )
            successful = True
        except Exception as e:
            response_data = e.__str__()
            successful = False
        if req.response:
            res = Response.create(req.request_id, response_data, successful)
            return res.to_bytes()
        return b""

    async def _new_connection(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        _ip = writer.transport.get_extra_info("peername")
        self.logger.info(f"[+] New Connection from {_ip}")
        while not self.stopped:
            try:
                requests = await reader.read(10000)
            except (BrokenPipeError, ConnectionResetError):
                break
            if not requests:
                break

            for request in requests.decode().split("\n"):
                if request:
                    self.logger.debug(f"= {request} =")
                response: bytes = await self._create_response(
                    bytes(request, "UTF-8")
                )
                if response:
                    writer.write(response)
                    await writer.drain()
        self.logger.info(f"[-] Disconnected from {_ip}")

    def add_route(self, **kwargs) -> Callable:
        """
        adds a route
        :return:
        """

        if "route" not in kwargs:
            raise InvalidRouteNameException("No route name provided.")

        def _wrapper(func: Callable) -> Callable:
            self.routes[kwargs["route"]] = func
            return func

        return _wrapper

    def __del__(self) -> None:
        self.stopped = True
        self.server.close()

    def close(self) -> None:
        """
        Closes the Server
        :return:
        """
        self.stopped = True
        self.server.close()
