# src/shared/middleware/AuthMiddleware.py
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any, Optional
from ..services.AuthService import AuthService
from ..exceptions.AuthExceptions import TokenExpiredException, TokenInvalidException

security = HTTPBearer(auto_error=False)

def get_auth_service():
    """Factory para obtener instancia de AuthService"""
    return AuthService()

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> Dict[str, Any]:
    """Middleware para obtener usuario actual desde el token"""
    
    # Verificar que se proporcionó el header de autorización
    if not credentials:
        print("[ERROR] No se proporcionó token de autorización")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autorización requerido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        token = credentials.credentials
        print(f"[DEBUG] Verificando token: {token[:20]}...")
        
        # Verificar y decodificar token
        payload = auth_service.verify_token(token, "access")
        
        print(f"[DEBUG] Usuario autenticado: {payload.get('sub')}")
        return payload
        
    except TokenExpiredException:
        print("[ERROR] Token expirado")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except TokenInvalidException as e:
        print(f"[ERROR] Token inválido: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        print(f"[ERROR] Error inesperado en autenticación: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo validar las credenciales",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    auth_service: AuthService = Depends(get_auth_service)
) -> Optional[Dict[str, Any]]:
    """Middleware opcional para obtener usuario (puede ser None)"""
    try:
        if not credentials:
            return None
        return await get_current_user(credentials, auth_service)
    except HTTPException:
        return None

async def get_user_from_request(request: Request) -> Optional[Dict[str, Any]]:
    """Obtener usuario directamente desde request (para debugging)"""
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        token = auth_header.replace("Bearer ", "")
        auth_service = AuthService()
        
        # Debug: mostrar token decodificado sin verificar
        decoded = auth_service.decode_token_without_verification(token)
        print(f"[DEBUG] Token decodificado: {decoded}")
        
        payload = auth_service.verify_token(token, "access")
        return payload
        
    except Exception as e:
        print(f"[ERROR] Error obteniendo usuario desde request: {e}")
        return None

def require_verified_email(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Middleware que requiere email verificado"""
    # Aquí podrías agregar lógica adicional para verificar email
    # Por ahora solo retorna el usuario
    return current_user

def require_admin(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Middleware que requiere rol de administrador"""
    # Aquí podrías verificar rol de admin en el payload
    # if current_user.get("role") != "admin":
    #     raise HTTPException(status_code=403, detail="Acceso denegado")
    return current_user