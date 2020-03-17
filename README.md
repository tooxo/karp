# KeepAliveRequestProtocol

[![PiPy](https://img.shields.io/pypi/v/karp?style=flat-square)](https://pypi.org/project/karp/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

A mix-in protocol between http and websocket. It combines the route-based navigation of http with the 
streamed aspects of websockets.

This is still an early stage of development, things can change heavily in the future.


## Requirements
`Python3.6+`

## Installation

#### Pip:
`pip install karp`

#### From Source:
```shell script
git clone --depth=1 https://github.com/tooxo/karp
cd karp/
pip install .
```

## Protocol Definition
### Request

| name                         | content                                      | length             |
| ---------------------------- | -------------------------------------------- | ------------------ |
| Header Text                  | `KARP_HEAD`                                  | 9                  |
| Route (case insensitive)     | *route name ([A-z\_])*                       | n/a                |
| Type (Request=0; Response=1) | 0                                            | 1                  |
| Response Wanted (0 or 1)     | 1                                            | 1                  |
| Request ID                   | *Request Identifier (16\* [0-9])*            | 16                 |
| Content_Length               | `C_LEN`                                      | 5                  |
| Content_Length               | *content length in num of bytes*             | n/a                |
| Data                         | `KARP_DATA`                                  | 9                  |
| Data                         | *request data encoded in base64*             | Content_Length     |
| End of Request               | `KARP_END`                                   | 7                  |

#### Meta

- Allowed chars: `[A-Za-z0-9+/=]`

## Response

| name                         | content                                       | length             |
| ---------------------------- | --------------------------------------------- | ------------------ |
| Header Text                  | `KARP_HEAD`                                   | 9                  |
| Type (Request=0; Response=1) | 1                                             | 1                  |
| Request Successful (1/0)*¹   | 1                                             | 1                  |
| Request ID                   | *Request Identifier (16\* [0-9])*             | 16                 |
| Content_Length               | `C_LEN`                                       | 5                  |
| Content_Length               | *content length in num of bytes*              | n/a                |
| Data                         | `KARP_DATA`                                   | 9                  |
| Data                         | *request data encoded in base64*              | Content_Length     |
| End of Request               | `KARP_END`                                    | 7                  |

*¹ = If the request was not successful, the data will be an error message.

#### Meta

- Allowed chars: [A-Za-z0-9+/=]
- Every Response/Request sent to the socket ends with `\n` as a command-separator.

## TODO:

* [ ] Add Getting Started to README
* [ ] Unit-Tests