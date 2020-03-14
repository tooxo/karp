"""
Request
"""

import re
import base64
import random


class InvalidRequestException(Exception):
    """
    Exception raised on invalid request
    """

    pass


class Request(object):
    """
    Request
    """

    VALID_REQUEST_REGEX = r"KARP_HEAD([A-z]+)0([0-9]{16})C_LEN([0-9]+)KARP_DATA([A-z0-9/+=]+)KARP_END"

    def __init__(self, route: str, request_id: str, b64_data: str) -> None:
        self._route = route.lower()
        self._request_id: str = request_id
        self._content_length: int = len(b64_data)
        self.b64_data: str = b64_data

        self._text: str = base64.b64decode(self.b64_data.encode()).decode()

    @classmethod
    def parse(cls, raw_data: bytes):
        """
        parse a request from raw
        :param raw_data:
        :return:
        """
        print(raw_data)
        match = re.match(Request.VALID_REQUEST_REGEX, raw_data.decode("UTF-8"))
        if not match:
            raise InvalidRequestException()

        self = cls(match.group(1), match.group(2), match.group(4))

        if not len(self.b64_data) == self._content_length:
            raise InvalidRequestException("Invalid Content_Length")
        return self

    @staticmethod
    def generate_id() -> str:
        """
        Generate id
        :return:
        """
        chars = list("0123456789")
        s = ""
        for x in range(16):
            s += random.choice(chars)
        return s

    @classmethod
    def create(cls, route: str, data: str):
        """
        Create request
        :param route:
        :param data:
        :return:
        """
        b64_e = base64.b64encode(data.encode()).decode()
        self = cls(route, Request.generate_id(), b64_e)
        return self

    @property
    def content_length(self) -> int:
        """
        Content_Length of the response
        :return:
        """
        return self._content_length

    @property
    def text(self) -> str:
        """
        Content of the response
        :return:
        """
        return self._text

    @property
    def content(self) -> str:
        """
        Content of the response
        :return:
        """
        return self._text

    @property
    def route(self) -> str:
        """
        Route
        :return:
        """
        return self._route

    @property
    def request_id(self) -> str:
        """
        req id
        :return:
        """
        return self._request_id

    def __bytes__(self) -> bytes:
        """
        tobytes
        :return:
        """
        return f"KARP_HEAD{self.route}0{self.request_id}C_LEN{self.content_length}KARP_DATA{self.b64_data}KARP_END\n"\
            .encode()

    def to_bytes(self) -> bytes:
        """
        sadjsapoijd
        :return:
        """
        return bytes(self)
