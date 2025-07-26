# src/shared/exceptions/common_exceptions.py

class NotFoundException(Exception):
    """Excepción para recursos no encontrados"""
    def __init__(self, message: str = "Recurso no encontrado"):
        self.message = message
        super().__init__(self.message)

class UnauthorizedException(Exception):
    """Excepción para accesos no autorizados"""
    def __init__(self, message: str = "No autorizado"):
        self.message = message
        super().__init__(self.message)

class ValidationException(Exception):
    """Excepción para errores de validación"""
    def __init__(self, message: str = "Error de validación"):
        self.message = message
        super().__init__(self.message)

class ForbiddenException(Exception):
    """Excepción para accesos prohibidos"""
    def __init__(self, message: str = "Acceso prohibido"):
        self.message = message
        super().__init__(self.message)

class ConflictException(Exception):
    """Excepción para conflictos de recursos"""
    def __init__(self, message: str = "Conflicto de recursos"):
        self.message = message
        super().__init__(self.message)