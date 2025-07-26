import re
import uuid
from typing import Dict, Any, Optional, List
from dataclasses import dataclass


@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    value: Optional[Any] = None


class ValidationUtils:
    """Utilidades de validación"""

    # Expresiones regulares
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    PASSWORD_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')
    PHONE_REGEX = re.compile(r'^\+?1?\d{9,15}$')

    @staticmethod
    def validate_email(email: str) -> ValidationResult:
        """Validar formato de email"""
        errors = []
        
        if not email:
            errors.append("El email es requerido")
        elif not ValidationUtils.EMAIL_REGEX.match(email):
            errors.append("Formato de email inválido")
        elif len(email) > 254:
            errors.append("El email es demasiado largo")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            value=email.lower().strip() if email else None
        )

    @staticmethod
    def validate_password(password: str) -> ValidationResult:
        """Validar contraseña"""
        errors = []
        
        if not password:
            errors.append("La contraseña es requerida")
        elif len(password) < 8:
            errors.append("La contraseña debe tener al menos 8 caracteres")
        elif len(password) > 128:
            errors.append("La contraseña es demasiado larga")
        else:
            if not re.search(r'[a-z]', password):
                errors.append("La contraseña debe tener al menos una minúscula")
            if not re.search(r'[A-Z]', password):
                errors.append("La contraseña debe tener al menos una mayúscula")
            if not re.search(r'\d', password):
                errors.append("La contraseña debe tener al menos un número")
            if not re.search(r'[@$!%*?&]', password):
                errors.append("La contraseña debe tener al menos un caracter especial")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            value=password
        )

    @staticmethod
    def validate_uuid(value: str) -> ValidationResult:
        """Validar UUID"""
        errors = []
        
        if not value:
            errors.append("El ID es requerido")
        else:
            try:
                uuid_obj = uuid.UUID(value)
                # Verificar que es UUID v4
                if uuid_obj.version != 4:
                    errors.append("Formato de UUID inválido")
            except ValueError:
                errors.append("Formato de UUID inválido")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            value=value
        )

    @staticmethod
    def validate_name(name: str, field_name: str = "nombre") -> ValidationResult:
        """Validar nombre"""
        errors = []
        
        if not name:
            errors.append(f"El {field_name} es requerido")
        elif len(name.strip()) < 2:
            errors.append(f"El {field_name} debe tener al menos 2 caracteres")
        elif len(name.strip()) > 100:
            errors.append(f"El {field_name} es demasiado largo")
        elif not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\-\'\.]+$', name.strip()):
            errors.append(f"El {field_name} contiene caracteres inválidos")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            value=name.strip().title() if name else None
        )

    @staticmethod
    def validate_phone(phone: str) -> ValidationResult:
        """Validar número de teléfono"""
        errors = []
        
        if not phone:
            errors.append("El teléfono es requerido")
        elif not ValidationUtils.PHONE_REGEX.match(phone):
            errors.append("Formato de teléfono inválido")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            value=phone.strip() if phone else None
        )

    @staticmethod
    def validate_age(age: int) -> ValidationResult:
        """Validar edad"""
        errors = []
        
        if age < 13:
            errors.append("Debes tener al menos 13 años")
        elif age > 120:
            errors.append("Edad inválida")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            value=age
        )

    @staticmethod
    def validate_pagination(page: int, limit: int) -> ValidationResult:
        """Validar parámetros de paginación"""
        errors = []
        
        if page < 1:
            errors.append("La página debe ser mayor a 0")
        
        if limit < 1:
            errors.append("El límite debe ser mayor a 0")
        elif limit > 100:
            errors.append("El límite no puede ser mayor a 100")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            value={"page": page, "limit": limit}
        )

    @staticmethod
    def sanitize_string(text: str, max_length: int = 255) -> str:
        """Sanitizar string"""
        if not text:
            return ""
        
        # Remover caracteres peligrosos
        sanitized = re.sub(r'[<>"\']', '', text.strip())
        
        # Truncar si es necesario
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
        
        return sanitized

    @staticmethod
    def validate_file_extension(filename: str, allowed_extensions: List[str]) -> ValidationResult:
        """Validar extensión de archivo"""
        errors = []
        
        if not filename:
            errors.append("El nombre del archivo es requerido")
        else:
            extension = filename.split('.')[-1].lower()
            if extension not in [ext.lower() for ext in allowed_extensions]:
                errors.append(f"Extensión no permitida. Permitidas: {', '.join(allowed_extensions)}")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            value=filename
        )