"""
KARP - Server
"""

import asyncio
import logging
import traceback
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Optional, Dict

from karp.utils import PendingRequest, Utils
from karp.request import Request
from karp.response import Response, InvalidResponseException

logging.basicConfig(level=logging.WARNING)


class InvalidRouteNameException(Exception):
    """
    Raised if route does not exist
    """

    pass


class Client:
    """
    Client
    """
    def __init__(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter, _id: str
    ):
        self.reader = reader
        self.writer = writer
        self.id = _id

        self.requests: Dict[str, PendingRequest] = {}

    async def request(
        self, route: str, data: str, response: bool = True, timeout: int = None
    ):
        """

        :param route:
        :param data:
        :param response:
        :param timeout:
        :return:
        """
        req: Request = Request.create(route, data, response)
        self.writer.write(req.to_bytes())

        if response:
            self.requests[req.request_id] = PendingRequest()
        await self.writer.drain()

        if not response:
            return

        try:
            response = await self.requests[req.request_id].process(
                timeout=timeout
            )
        except TimeoutError:
            del self.requests[req.request_id]
            raise

        del self.requests[req.request_id]
        return response


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

        self.clients: Dict[str, Client] = {}

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
            fun = self.routes[req.route]
            if asyncio.iscoroutinefunction(fun):
                response_data = await fun(req)
            else:
                response_data = await asyncio.get_event_loop().run_in_executor(
                    self.executor, self.routes[req.route], req
                )
            successful = True
        except (Exception, AssertionError) as e:
            if not req.response:
                self.logger.warning(traceback.format_exc(e))
            response_data = e.__str__()
            successful = False
        if req.response:
            res = Response.create(req.request_id, response_data, successful)
            return res.to_bytes()
        return b""

    def on_new_connection(
        self, client: Client
    ):
        """
        Called on new connection.
        :param client:
        :return:
        """
        pass

    def on_connection_lost(self, client: Client):
        """
        Called, when the connection gets lost
        :param client:
        :return:
        """
        pass

    async def _handle(self, request, writer, _id, _ip) -> None:
        try:
            r = Utils.create_interaction_object(request)
            if isinstance(r, Request):
                response: bytes = await self._create_response(
                    bytes(request, "UTF-8")
                )
                if response:
                    writer.write(response)
                    await writer.drain()
            else:
                if r.request_id in self.clients[_id].requests:
                    self.clients[_id].requests[r.request_id].complete(r)
        except InvalidResponseException:
            traceback.print_exc()

    async def _new_connection(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        _ip = writer.transport.get_extra_info("peername")
        _id = Request.generate_id()
        self.clients[_id] = Client(reader, writer, _id)
        if asyncio.iscoroutinefunction(self.on_new_connection):
            asyncio.ensure_future(self.on_new_connection(self.clients[_id]))
        else:
            asyncio.ensure_future(
                asyncio.get_event_loop().run_in_executor(
                    self.executor, self.on_new_connection, self.clients[_id]
                )
            )
        self.logger.info(f"[+] New Connection from {_ip}")
        while not self.stopped:
            try:
                requests = await reader.read(10000)
            except (BrokenPipeError, ConnectionResetError):
                break
            if not requests:
                break

            try:
                for request in requests.decode().split("\n"):
                    if request:
                        self.logger.debug(f"= {request} =")
                        asyncio.ensure_future(
                            self._handle(request, writer, _id, _ip)
                        )
            except UnicodeDecodeError:
                break

        if asyncio.iscoroutinefunction(self.on_connection_lost):
            asyncio.ensure_future(self.on_connection_lost(self.clients[_id]))
        else:
            asyncio.ensure_future(
                asyncio.get_event_loop().run_in_executor(
                    self.executor, self.on_connection_lost, self.clients[_id]
                )
            )
        del self.clients[_id]
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
