class InvalidCredentialsException(Exception):
    def __init__(self, message: str = "Credenciales inválidas"):
        self.message = message
        super().__init__(self.message)

class TokenExpiredException(Exception):
    def __init__(self, message: str = "Token expirado"):
        self.message = message
        super().__init__(self.message)

class TokenInvalidException(Exception):
    def __init__(self, message: str = "Token inválido"):
        self.message = message
        super().__init__(self.message)

class UserNotActiveException(Exception):
    def __init__(self, message: str = "Usuario no activo"):
        self.message = message
        super().__init__(self.message)