class EmailSendException(Exception):
    def __init__(self, message: str = "Error enviando email"):
        self.message = message
        super().__init__(self.message)

class EmailTemplateException(Exception):
    def __init__(self, message: str = "Error en template de email"):
        self.message = message
        super().__init__(self.message)

class EmailConfigurationException(Exception):
    def __init__(self, message: str = "Error de configuración de email"):
        self.message = message
        super().__init__(self.message)