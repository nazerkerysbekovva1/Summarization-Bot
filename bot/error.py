from typing import Dict

class Error(Exception):
    """Негізгі Error сыныбы, нақтырақ ештеңе қолданылмаған кезде қайтарылады"""

    def __init__(self, message=None) -> None:
        super(Error, self).__init__(message)

        self.message = message

    def __str__(self) -> str:
        msg = self.message or "<empty message>"
        return msg

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message={str(self)})"


class APIError(Error):
    """API қате туралы хабармен жауап бергенде қайтарылады"""

    def __init__(self, message: str = None, http_status: int = None, headers: Dict = None):
        super().__init__(message)
        self.http_status = http_status
        self.headers = headers or {}

    @classmethod
    def from_response(cls, response, message=None):
        return cls(message=message or response.text, http_status=response.status, headers=response.headers)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message={str(self)}, http_status={self.http_status})"

class ConnectionError(Error):
    """SDK қандай да бір себептермен API серверіне жете алмаған кезде қайтарылады"""