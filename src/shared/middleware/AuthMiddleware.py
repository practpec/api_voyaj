from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any
from ..services.AuthService import AuthService
from ..exceptions.AuthExceptions import TokenExpiredException, TokenInvalidException

security = HTTPBearer()
auth_service = AuthService()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Middleware para obtener usuario actual desde el token"""
    try:
        token = credentials.credentials
        payload = auth_service.verify_token(token, "access")
        return payload
        
    except TokenExpiredException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except TokenInvalidException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se pudo validar las credenciales",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_optional_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any] | None:
    """Middleware opcional para obtener usuario (puede ser None)"""
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None