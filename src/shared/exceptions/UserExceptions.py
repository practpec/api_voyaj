class UserNotFoundException(Exception):
    def __init__(self, message: str = "Usuario no encontrado"):
        self.message = message
        super().__init__(self.message)

class UserAlreadyExistsException(Exception):
    def __init__(self, message: str = "El usuario ya existe"):
        self.message = message
        super().__init__(self.message)

class UserNotActiveException(Exception):
    def __init__(self, message: str = "Usuario no activo"):
        self.message = message
        super().__init__(self.message)