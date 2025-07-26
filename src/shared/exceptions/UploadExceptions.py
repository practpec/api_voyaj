class FileTooLargeException(Exception):
    def __init__(self, message: str = "Archivo demasiado grande"):
        self.message = message
        super().__init__(self.message)

class InvalidFileTypeException(Exception):
    def __init__(self, message: str = "Tipo de archivo no válido"):
        self.message = message
        super().__init__(self.message)

class UploadFailedException(Exception):
    def __init__(self, message: str = "Error al subir archivo"):
        self.message = message
        super().__init__(self.message)

class CloudinaryException(Exception):
    def __init__(self, message: str = "Error en Cloudinary"):
        self.message = message
        super().__init__(self.message)