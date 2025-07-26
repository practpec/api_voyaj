import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from jose import JWTError, jwt
from ..exceptions.AuthExceptions import TokenExpiredException, TokenInvalidException

class AuthService:
    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_days = 7

    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Crear access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Crear refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """Verificar y decodificar token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            if payload.get("type") != token_type:
                raise TokenInvalidException("Tipo de token inválido")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise TokenExpiredException("Token expirado")
        except JWTError:
            raise TokenInvalidException("Token inválido")

    def refresh_access_token(self, refresh_token: str) -> str:
        """Generar nuevo access token usando refresh token"""
        payload = self.verify_token(refresh_token, "refresh")
        new_token_data = {"sub": payload["sub"]}
        return self.create_access_token(new_token_data)