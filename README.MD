# KeepAliveRequestProtocol

A mix-in protocol between http and websocket.
This is still an early stage of development, things can change heavily in the future.

## Request


| name | content | length |
| --- | --- | --- |
| Header Text | `KARP_HEAD` | 9 |
| Route (case insensitive) | _route name ([A-z_])_ | n/a |
| Type (Request=0; Response=1) | 0 | 1 |
| Request ID | _Request Identifier (16* [0-9])_ | 16 |
| Content_Length | `C_LEN` _content length in bytes_ | 5+ |
| Data | `KARP_DATA` _request data encoded in base64_ | 9 + Content_Length |
| End of Request | `KARP_END` | 7 |

#### Meta
Allowed chars: [A-Za-z0-9+/=]

## Response
| name | content | length |
| --- | --- | --- |
| Header Text | `KARP_HEAD` | 9 |
| Type (Request=0; Response=1) | 1 | 1 |
| Request ID | _Request Identifier (16* [0-9])_ | 16 |
| Content_Length | `C_LEN` _content length in bytes_  | 5+ |
| Data | `KARP_DATA` _response data encoded in base64_ | 9 + Content_Length |
| End of Request | `KARP_END` | 7 |

#### Meta
Allowed chars: [A-Za-z0-9+/=]
Every Response/Request socket send ends with `\n`

## TODO:
* Responses on failure [x]
* Error detection [x]
* No-Response Requests [x]
* logging [x]