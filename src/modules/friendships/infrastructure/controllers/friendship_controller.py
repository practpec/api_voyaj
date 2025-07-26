from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Annotated, List

from ...application.dtos.friendship_dto import (
    SendFriendRequestDTO, 
    FriendshipResponseDTO, 
    FriendListResponseDTO,
    FriendRequestResponseDTO,
    FriendSuggestionDTO
)
from ...application.use_cases.send_friend_request import SendFriendRequestUseCase
from ...application.use_cases.accept_friend_request import AcceptFriendRequestUseCase
from ...application.use_cases.reject_friend_request import RejectFriendRequestUseCase
from ...application.use_cases.remove_friendship import RemoveFriendshipUseCase
from ...application.use_cases.get_friends import GetFriendsUseCase
from ...application.use_cases.get_friend_requests import GetFriendRequestsUseCase
from ...application.use_cases.get_friend_suggestions import GetFriendSuggestionsUseCase
from ...application.use_cases.get_friendship_stats import GetFriendshipStatsUseCase, FriendshipStatsDTO
from shared.middleware.AuthMiddleware import get_current_user
from shared.utils.response_utils import SuccessResponse, PaginatedResponse
from shared.utils.validation_utils import ValidationUtils


class FriendshipController:
    def __init__(
        self,
        send_friend_request_use_case: SendFriendRequestUseCase,
        accept_friend_request_use_case: AcceptFriendRequestUseCase,
        reject_friend_request_use_case: RejectFriendRequestUseCase,
        remove_friendship_use_case: RemoveFriendshipUseCase,
        get_friends_use_case: GetFriendsUseCase,
        get_friend_requests_use_case: GetFriendRequestsUseCase,
        get_friend_suggestions_use_case: GetFriendSuggestionsUseCase,
        get_friendship_stats_use_case: GetFriendshipStatsUseCase
    ):
        self.router = APIRouter(prefix="/api/friendships", tags=["friendships"])
        self._send_friend_request_use_case = send_friend_request_use_case
        self._accept_friend_request_use_case = accept_friend_request_use_case
        self._reject_friend_request_use_case = reject_friend_request_use_case
        self._remove_friendship_use_case = remove_friendship_use_case
        self._get_friends_use_case = get_friends_use_case
        self._get_friend_requests_use_case = get_friend_requests_use_case
        self._get_friend_suggestions_use_case = get_friend_suggestions_use_case
        self._get_friendship_stats_use_case = get_friendship_stats_use_case
        
        self._register_routes()

    def _register_routes(self):
        """Registrar rutas del controlador"""
        
        @self.router.post("/request", response_model=SuccessResponse[FriendshipResponseDTO])
        async def send_friend_request(
            dto: SendFriendRequestDTO,
            current_user: Annotated[dict, Depends(get_current_user)]
        ):
            """Enviar solicitud de amistad"""
            try:
                # Validar entrada
                validation_result = ValidationUtils.validate_uuid(dto.friend_id)
                if not validation_result["is_valid"]:
                    raise HTTPException(status_code=400, detail="ID de usuario inválido")

                result = await self._send_friend_request_use_case.execute(dto, current_user["id"])
                
                return SuccessResponse(
                    data=result,
                    message="Solicitud de amistad enviada exitosamente"
                )
                
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail="Error interno del servidor")

        @self.router.put("/{friendship_id}/accept", response_model=SuccessResponse[FriendshipResponseDTO])
        async def accept_friend_request(
            friendship_id: str,
            current_user: Annotated[dict, Depends(get_current_user)]
        ):
            """Aceptar solicitud de amistad"""
            try:
                # Validar entrada
                validation_result = ValidationUtils.validate_uuid(friendship_id)
                if not validation_result["is_valid"]:
                    raise HTTPException(status_code=400, detail="ID de solicitud inválido")

                result = await self._accept_friend_request_use_case.execute(friendship_id, current_user["id"])
                
                return SuccessResponse(
                    data=result,
                    message="Solicitud de amistad aceptada exitosamente"
                )
                
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail="Error interno del servidor")

        @self.router.get("/", response_model=PaginatedResponse[FriendListResponseDTO])
        async def get_friends(
            current_user: Annotated[dict, Depends(get_current_user)],
            page: int = Query(1, ge=1, description="Número de página"),
            limit: int = Query(20, ge=1, le=100, description="Elementos por página")
        ):
            """Obtener lista de amigos"""
            try:
                result = await self._get_friends_use_case.execute(current_user["id"], page, limit)
                return result
                
            except Exception as e:
                raise HTTPException(status_code=500, detail="Error interno del servidor")

        @self.router.put("/{friendship_id}/reject", response_model=SuccessResponse[FriendshipResponseDTO])
        async def reject_friend_request(
            friendship_id: str,
            current_user: Annotated[dict, Depends(get_current_user)]
        ):
            """Rechazar solicitud de amistad"""
            try:
                validation_result = ValidationUtils.validate_uuid(friendship_id)
                if not validation_result["is_valid"]:
                    raise HTTPException(status_code=400, detail="ID de solicitud inválido")

                result = await self._reject_friend_request_use_case.execute(friendship_id, current_user["id"])
                
                return SuccessResponse(
                    data=result,
                    message="Solicitud de amistad rechazada exitosamente"
                )
                
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail="Error interno del servidor")

        @self.router.delete("/{friendship_id}", response_model=SuccessResponse[bool])
        async def remove_friendship(
            friendship_id: str,
            current_user: Annotated[dict, Depends(get_current_user)]
        ):
            """Eliminar amistad"""
            try:
                validation_result = ValidationUtils.validate_uuid(friendship_id)
                if not validation_result["is_valid"]:
                    raise HTTPException(status_code=400, detail="ID de amistad inválido")

                result = await self._remove_friendship_use_case.execute(friendship_id, current_user["id"])
                
                return SuccessResponse(
                    data=result,
                    message="Amistad eliminada exitosamente"
                )
                
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail="Error interno del servidor")

        @self.router.get("/requests/received", response_model=PaginatedResponse[FriendRequestResponseDTO])
        async def get_received_requests(
            current_user: Annotated[dict, Depends(get_current_user)],
            page: int = Query(1, ge=1, description="Número de página"),
            limit: int = Query(20, ge=1, le=100, description="Elementos por página")
        ):
            """Obtener solicitudes de amistad recibidas"""
            try:
                result = await self._get_friend_requests_use_case.execute_received(
                    current_user["id"], page, limit
                )
                return result
                
            except Exception as e:
                raise HTTPException(status_code=500, detail="Error interno del servidor")

        @self.router.get("/requests/sent", response_model=PaginatedResponse[FriendRequestResponseDTO])
        async def get_sent_requests(
            current_user: Annotated[dict, Depends(get_current_user)],
            page: int = Query(1, ge=1, description="Número de página"),
            limit: int = Query(20, ge=1, le=100, description="Elementos por página")
        ):
            """Obtener solicitudes de amistad enviadas"""
            try:
                result = await self._get_friend_requests_use_case.execute_sent(
                    current_user["id"], page, limit
                )
                return result
                
            except Exception as e:
                raise HTTPException(status_code=500, detail="Error interno del servidor")

        @self.router.get("/suggestions", response_model=SuccessResponse[List[FriendSuggestionDTO]])
        async def get_friend_suggestions(
            current_user: Annotated[dict, Depends(get_current_user)],
            limit: int = Query(10, ge=1, le=50, description="Número de sugerencias")
        ):
            """Obtener sugerencias de amigos"""
            try:
                result = await self._get_friend_suggestions_use_case.execute(
                    current_user["id"], limit
                )
                
                return SuccessResponse(
                    data=result,
                    message="Sugerencias obtenidas exitosamente"
                )
                
            except Exception as e:
                raise HTTPException(status_code=500, detail="Error interno del servidor")

        @self.router.get("/stats", response_model=SuccessResponse[FriendshipStatsDTO])
        async def get_friendship_stats(
            current_user: Annotated[dict, Depends(get_current_user)]
        ):
            """Obtener estadísticas de amistad"""
            try:
                result = await self._get_friendship_stats_use_case.execute(current_user["id"])
                
                return SuccessResponse(
                    data=result,
                    message="Estadísticas obtenidas exitosamente"
                )
                
            except Exception as e:
                raise HTTPException(status_code=500, detail="Error interno del servidor")