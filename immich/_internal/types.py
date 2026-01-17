from typing import Literal, Optional, Union

from pydantic import BaseModel

_MaybeBaseModel = Optional[Union[BaseModel, list[BaseModel]]]
_FormatMode = Literal["pretty", "json"]
