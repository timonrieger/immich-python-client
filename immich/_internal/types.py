from typing import Literal, Optional, Union

from pydantic import BaseModel

_MaybeBaseModel = Optional[Union[BaseModel, list[BaseModel]]]
_FormatMode = Literal["pretty", "json"]
_LogLevel = Literal["info", "warning", "error", "debug"]


class ClientConfig(BaseModel):
    """ "
    A configuration for a client to connect to an Immich server.
    """

    base_url: Optional[str]
    api_key: Optional[str]
    access_token: Optional[str]
