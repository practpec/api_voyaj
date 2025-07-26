from typing import Any, Optional, List, TypeVar, Generic
from dataclasses import dataclass
from datetime import datetime

T = TypeVar('T')


@dataclass
class SuccessResponse(Generic[T]):
    """Respuesta exitosa estándar"""
    data: T
    message: Optional[str] = None
    timestamp: datetime = None
    success: bool = True

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


@dataclass
class ErrorResponse:
    """Respuesta de error estándar"""
    success: bool = False
    error: str = ""
    message: str = ""
    details: Optional[Any] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


@dataclass
class PaginatedResponse(Generic[T]):
    """Respuesta paginada"""
    data: List[T]
    total: int
    page: int
    limit: int
    total_pages: int
    has_next: bool = False
    has_prev: bool = False
    success: bool = True
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        
        from math import ceil
        self.total_pages = ceil(self.total / self.limit) if self.limit > 0 else 0
        self.has_next = self.page < self.total_pages
        self.has_prev = self.page > 1


class ResponseUtils:
    """Utilidades para respuestas HTTP"""

    @staticmethod
    def success(data: T, message: Optional[str] = None) -> SuccessResponse[T]:
        """Crear respuesta exitosa"""
        return SuccessResponse(data=data, message=message)

    @staticmethod
    def error(error: str, message: str, details: Optional[Any] = None) -> ErrorResponse:
        """Crear respuesta de error"""
        return ErrorResponse(
            error=error,
            message=message,
            details=details
        )

    @staticmethod
    def paginated(
        data: List[T],
        total: int,
        page: int,
        limit: int
    ) -> PaginatedResponse[T]:
        """Crear respuesta paginada"""
        return PaginatedResponse(
            data=data,
            total=total,
            page=page,
            limit=limit,
            total_pages=0  # Se calcula en __post_init__
        )

    @staticmethod
    def created(data: T, message: str = "Recurso creado exitosamente") -> SuccessResponse[T]:
        """Respuesta de creación exitosa"""
        return ResponseUtils.success(data, message)

    @staticmethod
    def updated(data: T, message: str = "Recurso actualizado exitosamente") -> SuccessResponse[T]:
        """Respuesta de actualización exitosa"""
        return ResponseUtils.success(data, message)

    @staticmethod
    def deleted(message: str = "Recurso eliminado exitosamente") -> SuccessResponse[bool]:
        """Respuesta de eliminación exitosa"""
        return ResponseUtils.success(True, message)

    @staticmethod
    def not_found(message: str = "Recurso no encontrado") -> ErrorResponse:
        """Respuesta de recurso no encontrado"""
        return ResponseUtils.error("NOT_FOUND", message)

    @staticmethod
    def validation_error(message: str, details: Optional[Any] = None) -> ErrorResponse:
        """Respuesta de error de validación"""
        return ResponseUtils.error("VALIDATION_ERROR", message, details)

    @staticmethod
    def unauthorized(message: str = "No autorizado") -> ErrorResponse:
        """Respuesta de no autorizado"""
        return ResponseUtils.error("UNAUTHORIZED", message)

    @staticmethod
    def forbidden(message: str = "Acceso prohibido") -> ErrorResponse:
        """Respuesta de acceso prohibido"""
        return ResponseUtils.error("FORBIDDEN", message)

    @staticmethod
    def conflict(message: str = "Conflicto de recursos") -> ErrorResponse:
        """Respuesta de conflicto"""
        return ResponseUtils.error("CONFLICT", message)

    @staticmethod
    def internal_error(message: str = "Error interno del servidor") -> ErrorResponse:
        """Respuesta de error interno"""
        return ResponseUtils.error("INTERNAL_SERVER_ERROR", message)