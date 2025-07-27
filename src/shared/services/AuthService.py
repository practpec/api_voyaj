# src/shared/services/AuthService.py
import os
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
import jwt
from ..exceptions.AuthExceptions import TokenExpiredException, TokenInvalidException

class AuthService:
    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET_KEY", "your-super-secret-key-change-this-in-production")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = int(os.getenv("JWT_EXPIRATION_HOURS", "24")) * 60
        self.refresh_token_expire_days = int(os.getenv("REFRESH_TOKEN_EXPIRATION_DAYS", "30"))
        
        # Log de configuración para debug
        print(f"[INFO] AuthService inicializado:")
        print(f"  - Secret key configurada: {'✓' if self.secret_key != 'your-super-secret-key-change-this-in-production' else '⚠️  USAR CLAVE POR DEFECTO'}")
        print(f"  - Token expira en: {self.access_token_expire_minutes} minutos")

    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Crear access token"""
        to_encode = data.copy()
        
        # Usar timezone-aware datetime
        expire = datetime.now(timezone.utc) + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access"
        })
        
        token = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        print(f"[DEBUG] Token creado para usuario: {data.get('sub', 'unknown')}")
        return token

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Crear refresh token"""
        to_encode = data.copy()
        
        # Usar timezone-aware datetime
        expire = datetime.now(timezone.utc) + timedelta(days=self.refresh_token_expire_days)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "refresh"
        })
        
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """Verificar y decodificar token"""
        try:
            # Decodificar token
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm],
                options={"verify_exp": True}
            )
            
            # Verificar tipo de token
            if payload.get("type") != token_type:
                print(f"[ERROR] Tipo de token inválido. Esperado: {token_type}, Recibido: {payload.get('type')}")
                raise TokenInvalidException("Tipo de token inválido")
            
            # Verificar que el token tenga un subject
            if not payload.get("sub"):
                print("[ERROR] Token sin subject (sub)")
                raise TokenInvalidException("Token sin identificador de usuario")
            
            print(f"[DEBUG] Token verificado exitosamente para usuario: {payload.get('sub')}")
            return payload
            
        except jwt.ExpiredSignatureError:
            print("[ERROR] Token expirado")
            raise TokenExpiredException("Token expirado")
        except jwt.InvalidTokenError as e:
            print(f"[ERROR] Token inválido: {str(e)}")
            raise TokenInvalidException(f"Token inválido: {str(e)}")
        except Exception as e:
            print(f"[ERROR] Error inesperado verificando token: {str(e)}")
            raise TokenInvalidException(f"Error verificando token: {str(e)}")

    def refresh_access_token(self, refresh_token: str) -> str:
        """Generar nuevo access token usando refresh token"""
        payload = self.verify_token(refresh_token, "refresh")
        new_token_data = {"sub": payload["sub"]}
        return self.create_access_token(new_token_data)

    def decode_token_without_verification(self, token: str) -> Dict[str, Any]:
        """Decodificar token sin verificar (solo para debug)"""
        try:
            return jwt.decode(token, options={"verify_signature": False})
        except Exception as e:
            print(f"[ERROR] No se pudo decodificar token: {e}")
            return {}