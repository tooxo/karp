"""
Client
"""
import asyncio
import traceback
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Dict, Optional, Callable

import karp.utils as utils
from karp.request import Request
from karp.response import InvalidResponseException, Response
from karp.server import InvalidRouteNameException


class KARPClient(object):
    """
    KARPClient
    """

    def __init__(self, hostname: str, port: str):
        """
        KARP Client
        :param hostname: to connect to
        :param port: to connect to
        """
        self.hostname = hostname
        self.port = port

        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None

        self.executor = ThreadPoolExecutor(max_workers=5)

        self.routes: dict = {}

        self._requests: Dict[str, utils.PendingRequest] = {}

    async def _create_response(self, request: bytes) -> bytes:
        if not request:
            return b""
        req: Request = Request.parse(request)
        try:
            func = self.routes[req.route]
            if asyncio.iscoroutinefunction(func):
                response_data = await func(req)
            else:
                response_data = await asyncio.get_event_loop().run_in_executor(
                    self.executor, self.routes[req.route], req
                )
            successful = True
        except Exception as e:
            if req.response:
                traceback.print_exc()
            response_data = e.__str__()
            successful = False
        if req.response:
            res = Response.create(req.request_id, response_data, successful)
            return res.to_bytes()
        return b""

    async def _handle(self, response) -> None:
        try:
            r = utils.Utils.create_interaction_object(response)
            if isinstance(r, Request):
                res: bytes = await self._create_response(bytes(r))
                if res:
                    self.writer.write(res)
                    await self.writer.drain()
            else:
                if r.request_id in self._requests:
                    self._requests[r.request_id].complete(r)
        except InvalidResponseException:
            traceback.print_exc()

    async def _read(self) -> None:
        while True:
            try:
                responses: bytes = await self.reader.read(100000)
            except BrokenPipeError:
                break
            if not responses:
                break

            for response in responses.decode().split("\n"):
                if response:
                    asyncio.ensure_future(self._handle(response))

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

    async def open(self) -> asyncio.Future:
        """
        Open the connection
        :return:
        """

        self.reader, self.writer = await asyncio.open_connection(
            self.hostname, self.port
        )
        return asyncio.ensure_future(self._read())

    async def request(
        self, route: str, request_data: str, timeout=None, response=True,
    ) -> Optional[Response]:
        """
        Request something
        :param route:
        :param request_data:
        :param timeout: Timeout, None for infinite, raises TimeoutError on failure
        :param response: wait for a response
        :return:
        """
        req = Request.create(route, request_data, response)

        self.writer.write(req.to_bytes())
        if response:
            self._requests[req.request_id] = utils.PendingRequest()

        await self.writer.drain()

        if not response:
            return

        try:
            response = await self._requests[req.request_id].process(
                timeout=timeout
            )
        except TimeoutError:
            del self._requests[req.request_id]
            raise

        del self._requests[req.request_id]
        return response
