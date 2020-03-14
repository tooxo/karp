"""
Client
"""
import asyncio
import traceback
from typing import Optional, Dict
from karp.response import Response, InvalidResponseException
from karp.request import Request


class PendingRequest:
    def __init__(self):
        self.response: Optional[Response] = None
        self.event = asyncio.Event()

    async def process(self) -> Response:
        """

        :return:
        """
        await self.event.wait()
        return self.response

    def complete(self, response: Response):
        """

        :param response:
        :return:
        """
        self.response = response
        self.event.set()


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

        self.requests: Dict[str, PendingRequest] = {}

    async def _read(self) -> None:
        while True:
            try:
                responses: bytes = await self.reader.read(100000)
            except BrokenPipeError:
                break
            if not responses:
                break

            for response in responses.decode().split("\n"):
                try:
                    res = Response.parse(bytes(response, "UTF-8"))
                    self.requests[res.request_id].complete(res)
                except InvalidResponseException as e:
                    traceback.print_exc()

    async def open(self) -> asyncio.Future:
        """

        :return:
        """

        self.reader, self.writer = await asyncio.open_connection(
            self.hostname, self.port
        )
        return asyncio.ensure_future(self._read())

    async def request(self, route: str, request_data: str) -> Response:
        """
        Request something
        :param route:
        :param request_data:
        :return:
        """
        req = Request.create(route, request_data)

        self.writer.write(req.to_bytes())
        self.requests[req.request_id] = PendingRequest()

        await self.writer.drain()

        response = await self.requests[req.request_id].process()

        del self.requests[req.request_id]
        return response
