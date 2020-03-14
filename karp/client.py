"""
Client
"""
import asyncio
import traceback
from typing import Dict, Optional

from karp.request import Request
from karp.response import InvalidResponseException, Response


class PendingRequest:
    """
    PendingRequest
    """

    def __init__(self) -> None:
        self.response: Optional[Response] = None
        self.event = asyncio.Event()

    async def process(self, timeout: Optional[float] = None) -> Response:
        """
        Wait for the request to be finished.
        :return:
        """
        await asyncio.wait_for(self.event.wait(), timeout)
        return self.response

    def complete(self, response: Response) -> None:
        """
        Complete the pending request.
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

        self._requests: Dict[str, PendingRequest] = {}

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
                    if res:
                        if res.request_id in self._requests:
                            self._requests[res.request_id].complete(res)
                except InvalidResponseException:
                    traceback.print_exc()

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
        self, route: str, request_data: str, timeout=None
    ) -> Response:
        """
        Request something
        :param route:
        :param request_data:
        :param timeout: Timeout, None for infinite, raises TimeoutError on failure
        :return:
        """
        req = Request.create(route, request_data)

        self.writer.write(req.to_bytes())
        self._requests[req.request_id] = PendingRequest()

        await self.writer.drain()

        try:
            response = await self._requests[req.request_id].process(
                timeout=timeout
            )
        except TimeoutError:
            del self._requests[req.request_id]
            raise

        del self._requests[req.request_id]
        return response
