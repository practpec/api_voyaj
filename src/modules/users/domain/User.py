from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from uuid import uuid4
from passlib.context import CryptContext
import secrets
import string

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User:
    def __init__(
        self,
        correo_electronico: str,
        nombre: str,
        contrasena: str,
        user_id: Optional[str] = None,
        url_foto_perfil: Optional[str] = None,
        telefono: Optional[str] = None,
        pais: Optional[str] = None,
        ciudad: Optional[str] = None,
        fecha_nacimiento: Optional[datetime] = None,
        biografia: Optional[str] = None,
        preferencias: Optional[Dict[str, Any]] = None,
        esta_activo: bool = True,
        email_verificado: bool = False,
        plan: str = "free",
        creado_en: Optional[datetime] = None,
        ultimo_acceso: Optional[datetime] = None,
        eliminado: bool = False,
        codigo_verificacion_email: Optional[str] = None,
        codigo_verificacion_email_expira: Optional[datetime] = None,
        codigo_recuperacion_password: Optional[str] = None,
        codigo_recuperacion_password_expira: Optional[datetime] = None
    ):
        self.id = user_id or str(uuid4())
        self.correo_electronico = correo_electronico.lower()
        self.nombre = nombre
        self._contrasena_hash = self._hash_password(contrasena)
        self.url_foto_perfil = url_foto_perfil
        self.telefono = telefono
        self.pais = pais
        self.ciudad = ciudad
        self.fecha_nacimiento = fecha_nacimiento
        self.biografia = biografia
        self.preferencias = preferencias or {}
        self.esta_activo = esta_activo
        self.email_verificado = email_verificado
        self.plan = plan
        self.creado_en = creado_en or datetime.utcnow()
        self.ultimo_acceso = ultimo_acceso
        self.eliminado = eliminado
        self.actualizado_en = datetime.utcnow()
        
        # Campos para verificación de email
        self.codigo_verificacion_email = codigo_verificacion_email
        self.codigo_verificacion_email_expira = codigo_verificacion_email_expira
        
        # Campos para recuperación de contraseña
        self.codigo_recuperacion_password = codigo_recuperacion_password
        self.codigo_recuperacion_password_expira = codigo_recuperacion_password_expira

    def _hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def _generate_secure_code(self, length: int = 6) -> str:
        """Generar código seguro de verificación"""
        return ''.join(secrets.choice(string.digits) for _ in range(length))

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self._contrasena_hash)

    def update_password(self, new_password: str) -> None:
        self._contrasena_hash = self._hash_password(new_password)
        self.actualizado_en = datetime.utcnow()

    def update_profile(self, nombre: Optional[str] = None, url_foto_perfil: Optional[str] = None) -> None:
        if nombre is not None:
            self.nombre = nombre
        if url_foto_perfil is not None:
            self.url_foto_perfil = url_foto_perfil
        self.actualizado_en = datetime.utcnow()

    def update_extended_profile(
        self,
        telefono: Optional[str] = None,
        pais: Optional[str] = None,
        ciudad: Optional[str] = None,
        fecha_nacimiento: Optional[datetime] = None,
        biografia: Optional[str] = None
    ) -> None:
        if telefono is not None:
            self.telefono = telefono
        if pais is not None:
            self.pais = pais
        if ciudad is not None:
            self.ciudad = ciudad
        if fecha_nacimiento is not None:
            self.fecha_nacimiento = fecha_nacimiento
        if biografia is not None:
            self.biografia = biografia
        self.actualizado_en = datetime.utcnow()

    def generate_email_verification_code(self) -> str:
        """Generar código de verificación de email"""
        code = self._generate_secure_code(6)
        expires_at = datetime.utcnow() + timedelta(hours=24)
        
        self.codigo_verificacion_email = code
        self.codigo_verificacion_email_expira = expires_at
        self.actualizado_en = datetime.utcnow()
        
        return code

    def verify_email_code(self, code: str) -> bool:
        """Verificar código de email"""
        if not self.codigo_verificacion_email:
            return False
        
        if (not self.codigo_verificacion_email_expira or 
            self.codigo_verificacion_email_expira < datetime.utcnow()):
            return False
        
        if self.codigo_verificacion_email != code:
            return False
        
        # Marcar email como verificado y limpiar código
        self.email_verificado = True
        self.codigo_verificacion_email = None
        self.codigo_verificacion_email_expira = None
        self.actualizado_en = datetime.utcnow()
        
        return True

    def generate_password_reset_code(self) -> str:
        """Generar código de recuperación de contraseña"""
        code = self._generate_secure_code(6)
        expires_at = datetime.utcnow() + timedelta(minutes=10)
        
        self.codigo_recuperacion_password = code
        self.codigo_recuperacion_password_expira = expires_at
        self.actualizado_en = datetime.utcnow()
        
        return code

    def verify_password_reset_code(self, code: str) -> bool:
        """Verificar código de recuperación de contraseña"""
        if not self.codigo_recuperacion_password:
            return False
        
        if (not self.codigo_recuperacion_password_expira or 
            self.codigo_recuperacion_password_expira < datetime.utcnow()):
            return False
        
        if self.codigo_recuperacion_password != code:
            return False
        
        return True

    def reset_password_with_code(self, code: str, new_password: str) -> bool:
        """Resetear contraseña usando código de verificación"""
        if not self.verify_password_reset_code(code):
            return False
        
        # Actualizar contraseña y limpiar código
        self.update_password(new_password)
        self.codigo_recuperacion_password = None
        self.codigo_recuperacion_password_expira = None
        self.actualizado_en = datetime.utcnow()
        
        return True

    def verify_email(self) -> None:
        self.email_verificado = True
        self.actualizado_en = datetime.utcnow()

    def update_last_access(self) -> None:
        self.ultimo_acceso = datetime.utcnow()

    def soft_delete(self) -> None:
        self.eliminado = True
        self.esta_activo = False
        self.actualizado_en = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "correo_electronico": self.correo_electronico,
            "nombre": self.nombre,
            "url_foto_perfil": self.url_foto_perfil,
            "telefono": self.telefono,
            "pais": self.pais,
            "ciudad": self.ciudad,
            "fecha_nacimiento": self.fecha_nacimiento,
            "biografia": self.biografia,
            "preferencias": self.preferencias,
            "esta_activo": self.esta_activo,
            "email_verificado": self.email_verificado,
            "plan": self.plan,
            "creado_en": self.creado_en,
            "ultimo_acceso": self.ultimo_acceso,
            "eliminado": self.eliminado,
            "actualizado_en": self.actualizado_en,
            "codigo_verificacion_email": self.codigo_verificacion_email,
            "codigo_verificacion_email_expira": self.codigo_verificacion_email_expira,
            "codigo_recuperacion_password": self.codigo_recuperacion_password,
            "codigo_recuperacion_password_expira": self.codigo_recuperacion_password_expira
        }

    def to_public_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "correo_electronico": self.correo_electronico,
            "nombre": self.nombre,
            "url_foto_perfil": self.url_foto_perfil,
            "creado_en": self.creado_en
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        user = cls.__new__(cls)
        user.id = data["id"]
        user.correo_electronico = data["correo_electronico"]
        user.nombre = data["nombre"]
        user._contrasena_hash = data.get("contrasena_hash", "")
        user.url_foto_perfil = data.get("url_foto_perfil")
        user.telefono = data.get("telefono")
        user.pais = data.get("pais")
        user.ciudad = data.get("ciudad")
        user.fecha_nacimiento = data.get("fecha_nacimiento")
        user.biografia = data.get("biografia")
        user.preferencias = data.get("preferencias", {})
        user.esta_activo = data.get("esta_activo", True)
        user.email_verificado = data.get("email_verificado", False)
        user.plan = data.get("plan", "free")
        user.creado_en = data.get("creado_en")
        user.ultimo_acceso = data.get("ultimo_acceso")
        user.eliminado = data.get("eliminado", False)
        user.actualizado_en = data.get("actualizado_en")
        
        # Campos de verificación
        user.codigo_verificacion_email = data.get("codigo_verificacion_email")
        user.codigo_verificacion_email_expira = data.get("codigo_verificacion_email_expira")
        user.codigo_recuperacion_password = data.get("codigo_recuperacion_password")
        user.codigo_recuperacion_password_expira = data.get("codigo_recuperacion_password_expira")
        
        return user