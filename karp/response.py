"""
Response
"""

import re
import base64


class InvalidResponseException(Exception):
    """
    Exception raised on invalid response
    """

    pass


class Response(object):
    RESPONSE_VALID_REGEX = (
        r"KARP_HEAD1([0-9]{16})C_LEN([0-9]+)KARP_DATA([A-z0-9/+=]+)KARP_END"
    )

    def __init__(self, request_id: str, b64_data: str) -> None:
        self._request_id: str = request_id
        self._b64_data: str = b64_data
        self._content_length: int = len(b64_data)
        self._text: str = base64.b64decode(b64_data.encode()).decode()

    @classmethod
    def parse(cls, raw_bytes: bytes):
        if not raw_bytes:
            return
        match = re.match(Response.RESPONSE_VALID_REGEX, raw_bytes.decode())
        if not match:
            raise InvalidResponseException()

        self = cls(match.group(1), match.group(3))
        if not len(self._b64_data) == self._content_length:
            raise InvalidResponseException("Invalid Content_Length")
        return self

    @classmethod
    def create(cls, request_id: str, data: str):
        """
        Create request
        :param request_id:
        :param data:
        :return:
        """
        b64_e = base64.b64encode(data.encode()).decode()
        self = cls(request_id, b64_e)
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
        req id
        :return:
        """
        return self._request_id

    def __bytes__(self) -> bytes:
        """
        tobytes
        :return:
        """
        return f"KARP_HEAD1{self.request_id}C_LEN{self.content_length}KARP_DATA{self._b64_data}KARP_END\n".encode()

    def to_bytes(self) -> bytes:
        """
        sadjsapoijd
        :return:
        """
        return bytes(self)
