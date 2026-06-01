from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from src.model.exceptions import NotFoundError, ValidationError
import traceback
import logging

logger = logging.getLogger(__name__)


async def validation_error_handler(request: Request, exc: ValidationError) -> JSONResponse:
    logger.warning(f"Validation error on {request.url}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "status": "error",
            "error": "validation_error",
            "message": str(exc),
        }
    )

async def not_found_error_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    logger.info(f"Not found on {request.url}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "status": "error",
            "error": "not_found",
            "message": str(exc),
        },
    )


async def request_validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    logger.warning(f"Request validation error on {request.url}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "status": "error",
            "error": "request_validation_error",
            "message": "Invalid request",
            "details": {"errors": exc.errors()},
        },
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(
        f"Unhandled exception on {request.url}:\n{traceback.format_exc()}"
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "error": "internal_server_error",
            "message": "Произошла непредвиденная ошибка. Попробуйте позже.",
        }
    )


def register_exception_handlers(app):
    app.add_exception_handler(ValidationError, validation_error_handler)
    app.add_exception_handler(NotFoundError, not_found_error_handler)
    app.add_exception_handler(RequestValidationError, request_validation_error_handler)
    app.add_exception_handler(Exception, general_exception_handler)
