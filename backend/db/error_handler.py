from pydantic import BaseModel
from typing import Type
from sqlalchemy.orm.exc import NoResultFound
from typing import List, Callable
from sqlalchemy.ext.asyncio import AsyncSession
from logging_settings import get_logger
from fastapi import HTTPException


logger = get_logger(__name__)


class ErrorMapping(BaseModel):
    exception: Type[Exception]
    status_code: int
    detail: str


MapNoResultFound = ErrorMapping(
    exception=NoResultFound, status_code=404, detail='No result found'
)


def handle_error(
    mapping_exception: List[ErrorMapping] | None = None,
    log_error: bool = True,
    rollback: bool = False,
):
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
            except Exception as e:
                if rollback:
                    for item in args + tuple(kwargs.values()):
                        if isinstance(item, AsyncSession):
                            await item.rollback()

                for response in mapping_exception:
                    if isinstance(e, response.exception):
                        raise HTTPException(
                            status_code=response.status_code,
                            detail=response.detail,
                        )

                if log_error:
                    logger.error(func.__name__ + ' ' + str(e))

                raise HTTPException(status_code=500, detail='Unknown error occurred')
            return result

        return wrapper

    return decorator
