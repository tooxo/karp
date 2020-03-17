"""
Utils
"""
import asyncio
from typing import Union, Optional
from karp.response import Response
from karp.request import Request, InvalidRequestException


class Utils:
    """
    Utils
    """

    @staticmethod
    def create_interaction_object(
        unknown_object: str
    ) -> Union[Request, Response, None]:
        """

        :return:
        """
        try:
            return Request.parse(unknown_object.encode())
        except InvalidRequestException:
            return Response.parse(unknown_object.encode())


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
