# src/shared/errors/custom_errors.py
from typing import Any, Optional
from datetime import datetime


class AppError(Exception):
    """Clase base para errores de aplicación"""
    
    def __init__(
        self,
        message: str,
        status_code: int,
        error_code: str,
        is_operational: bool = True,
        details: Optional[Any] = None
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.is_operational = is_operational
        self.details = details
        self.timestamp = datetime.utcnow()


class ValidationError(AppError):
    """Error de validación"""
    
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=400,
            error_code="VALIDATION_ERROR",
            is_operational=True,
            details=details
        )


class AuthenticationError(AppError):
    """Error de autenticación"""
    
    def __init__(self, message: str, error_code: str = "INVALID_CREDENTIALS"):
        super().__init__(
            message=message,
            status_code=401,
            error_code=error_code,
            is_operational=True
        )


class AuthorizationError(AppError):
    """Error de autorización"""
    
    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=403,
            error_code="FORBIDDEN",
            is_operational=True
        )


class NotFoundError(AppError):
    """Error de recurso no encontrado"""
    
    def __init__(self, message: str, error_code: str = "NOT_FOUND"):
        super().__init__(
            message=message,
            status_code=404,
            error_code=error_code,
            is_operational=True
        )


class ConflictError(AppError):
    """Error de conflicto"""
    
    def __init__(self, message: str, error_code: str = "CONFLICT"):
        super().__init__(
            message=message,
            status_code=409,
            error_code=error_code,
            is_operational=True
        )


class RateLimitError(AppError):
    """Error de límite de velocidad"""
    
    def __init__(self, message: str = "Demasiadas peticiones"):
        super().__init__(
            message=message,
            status_code=429,
            error_code="RATE_LIMIT_EXCEEDED",
            is_operational=True
        )


class DatabaseError(AppError):
    """Error de base de datos"""
    
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=500,
            error_code="DATABASE_ERROR",
            is_operational=False,
            details=details
        )


class InternalServerError(AppError):
    """Error interno del servidor"""
    
    def __init__(self, message: str = "Error interno del servidor", details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=500,
            error_code="INTERNAL_SERVER_ERROR",
            is_operational=False,
            details=details
        )


class ErrorHandler:
    """Manejador de errores centralizado"""

    @staticmethod
    def create_conflict_error(message: str = "Conflicto de recursos") -> ConflictError:
        return ConflictError(message)

    @staticmethod
    def create_database_error(message: str, details: Optional[Any] = None) -> DatabaseError:
        return DatabaseError(message, details)

    @staticmethod
    def create_internal_error(message: str = "Error interno del servidor") -> InternalServerError:
        return InternalServerError(message)

    @staticmethod
    def create_rate_limit_error(message: str = "Demasiadas peticiones") -> RateLimitError:
        return RateLimitError(message)

    @staticmethod
    def handle_error(error: Exception) -> dict:
        """Manejar errores y convertir a diccionario"""
        if isinstance(error, AppError):
            return {
                "message": error.message,
                "status_code": error.status_code,
                "error_code": error.error_code,
                "timestamp": error.timestamp.isoformat(),
                "details": error.details
            }
        else:
            # Error no controlado
            return {
                "message": "Error interno del servidor",
                "status_code": 500,
                "error_code": "INTERNAL_SERVER_ERROR",
                "timestamp": datetime.utcnow().isoformat(),
                "details": str(error)
            }