from fastapi import HTTPException


class HTTPUnknownException(HTTPException):
    def __init__(self, detail="Unknown Error", status_code=500):
        super().__init__(status_code=status_code, detail=detail)

class HTTPNoResultFound(HTTPException):
    def __init__(self, status_code=404, detail="Object not found in Database"):
        super().__init__(status_code=status_code, detail=detail)