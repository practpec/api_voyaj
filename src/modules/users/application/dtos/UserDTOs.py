from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, Dict, Any, List

class CreateUserDTO(BaseModel):
    correo_electronico: EmailStr
    nombre: str = Field(..., min_length=2, max_length=100)
    contrasena: str = Field(..., min_length=8, max_length=100)

class LoginDTO(BaseModel):
    correo_electronico: EmailStr
    contrasena: str

class UpdateProfileDTO(BaseModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=100)
    url_foto_perfil: Optional[str] = None
    telefono: Optional[str] = None
    pais: Optional[str] = None
    ciudad: Optional[str] = None
    fecha_nacimiento: Optional[datetime] = None
    biografia: Optional[str] = Field(None, max_length=500)

class ChangePasswordDTO(BaseModel):
    contrasena_actual: str
    nueva_contrasena: str = Field(..., min_length=8, max_length=100)

class VerifyEmailDTO(BaseModel):
    correo_electronico: EmailStr
    codigo: str = Field(..., min_length=6, max_length=6)

class ResendVerificationDTO(BaseModel):
    correo_electronico: EmailStr

class RequestPasswordResetDTO(BaseModel):
    correo_electronico: EmailStr

class ResetPasswordDTO(BaseModel):
    correo_electronico: EmailStr
    codigo: str = Field(..., min_length=6, max_length=6)
    nueva_contrasena: str = Field(..., min_length=8, max_length=100)

class AuthenticatedUserDTO(BaseModel):
    id: str
    correo_electronico: str
    nombre: str
    url_foto_perfil: Optional[str] = None
    telefono: Optional[str] = None
    pais: Optional[str] = None
    ciudad: Optional[str] = None
    fecha_nacimiento: Optional[datetime] = None
    biografia: Optional[str] = None
    preferencias: Dict[str, Any] = {}
    esta_activo: bool
    email_verificado: bool
    plan: str
    creado_en: datetime
    ultimo_acceso: Optional[datetime] = None

class PublicUserDTO(BaseModel):
    id: str
    correo_electronico: str
    nombre: str
    url_foto_perfil: Optional[str] = None
    creado_en: datetime

class AuthResponseDTO(BaseModel):
    user: AuthenticatedUserDTO
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserSearchResultDTO(BaseModel):
    id: str
    correo_electronico: str
    nombre: str
    url_foto_perfil: Optional[str] = None

class SearchUsersResponseDTO(BaseModel):
    users: List[UserSearchResultDTO]
    total: int
    page: int
    limit: int