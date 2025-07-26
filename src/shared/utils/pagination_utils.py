from dataclasses import dataclass
from typing import List, TypeVar, Generic
from math import ceil

T = TypeVar('T')


@dataclass
class PaginatedResponse(Generic[T]):
    """Respuesta paginada genérica"""
    data: List[T]
    total: int
    page: int
    limit: int
    total_pages: int
    has_next: bool = False
    has_prev: bool = False

    def __post_init__(self):
        self.total_pages = ceil(self.total / self.limit) if self.limit > 0 else 0
        self.has_next = self.page < self.total_pages
        self.has_prev = self.page > 1


class PaginationUtils:
    """Utilidades para paginación"""
    
    DEFAULT_PAGE = 1
    DEFAULT_LIMIT = 20
    MAX_LIMIT = 100

    @staticmethod
    def validate_pagination(page: int, limit: int) -> tuple[int, int]:
        """Validar y normalizar parámetros de paginación"""
        # Validar página
        if page < 1:
            page = PaginationUtils.DEFAULT_PAGE

        # Validar límite
        if limit < 1:
            limit = PaginationUtils.DEFAULT_LIMIT
        elif limit > PaginationUtils.MAX_LIMIT:
            limit = PaginationUtils.MAX_LIMIT

        return page, limit

    @staticmethod
    def calculate_skip(page: int, limit: int) -> int:
        """Calcular número de documentos a saltar"""
        return (page - 1) * limit

    @staticmethod
    def create_paginated_response(
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
            total_pages=ceil(total / limit) if limit > 0 else 0
        )