from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from datetime import datetime
import traceback
from ..errors.custom_errors import AppError

class ErrorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except AppError as e:
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "success": False,
                    "error": e.error_code,
                    "message": e.message,
                    "details": e.details,
                    "timestamp": e.timestamp.isoformat()
                }
            )
        except Exception as e:
            error_id = str(datetime.utcnow().timestamp())
            print(f"[{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}] [ERROR_MIDDLEWARE] [ERROR] Error no controlado ID:{error_id} - {str(e)}")
            print(traceback.format_exc())
            
            return JSONResponse(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "success": False,
                    "error": "INTERNAL_SERVER_ERROR",
                    "message": "Error interno del servidor",
                    "error_id": error_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )