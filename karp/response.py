"""
Response
"""

import base64
import re


class InvalidResponseException(Exception):
    """
    Exception raised on invalid response
    """

    pass


class Response(object):
    """
    Response
    """

    RESPONSE_VALID_REGEX = re.compile(
        r"KARP_HEAD1([01])([0-9]{16})C_LEN([0-9]+)KARP_DATA([A-z0-9/+=]*)KARP_END"
    )

    def __init__(
        self, request_id: str, b64_data: str, successful: bool
    ) -> None:
        self._request_id: str = request_id
        self._b64_data: str = b64_data
        self._content_length: int = len(b64_data)
        self._text: str = base64.b64decode(b64_data.encode()).decode()

        self._successful = successful

    @classmethod
    def parse(cls, raw_bytes: bytes):
        """
        Parse raw bytes
        :param raw_bytes: raw bytes
        :return:
        """
        if not raw_bytes:
            return
        match = re.match(Response.RESPONSE_VALID_REGEX, raw_bytes.decode())
        if not match:
            raise InvalidResponseException()

        self = cls(match.group(2), match.group(4), match.group(1) == "1")
        if not len(self._b64_data) == self._content_length:
            raise InvalidResponseException("Invalid Content_Length")
        return self

    @classmethod
    def create(cls, request_id: str, data: str, successful: bool):
        """
        Create request
        :param request_id: request id
        :param data: data
        :param successful: check if the request was successful
        :return:
        """
        b64_e = base64.b64encode(data.encode()).decode()
        self = cls(request_id, b64_e, successful)
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
    def request_id(self) -> str:
        """
        Request Id
        :return:
        """
        return self._request_id

    def __bytes__(self) -> bytes:
        """
        Response as bytes
        :return:
        """
        return f"KARP_HEAD1{int(self.successful)}{self.request_id}C_LEN{self.content_length}KARP_DATA{self._b64_data}KARP_END\n".encode()

    def to_bytes(self) -> bytes:
        """
        Response as bytes
        :return:
        """
        return bytes(self)

    @property
    def successful(self) -> bool:
        """
        Return if the request was successful
        :return:
        """
        return self._successful

    def __str__(self) -> str:
        return str(self.__dict__)
