from typing import Any, Dict, Optional

from fastapi import HTTPException
from starlette import status


class Http404(HTTPException):
    def __init__(
        self, detail: Any = None, headers: Optional[Dict[str, str]] = None
    ) -> None:
        if detail is None:
            detail = "Объект не найден"
        super().__init__(status.HTTP_404_NOT_FOUND, detail, headers)

