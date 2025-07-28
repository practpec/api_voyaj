# src/modules/friendships/infrastructure/controllers/friendship_controller.py
from fastapi import HTTPException
from typing import Dict

from ...application.dtos.friendship_dto import SendFriendRequestDTO
from ...application.use_cases.send_friend_request import SendFriendRequestUseCase
from ...application.use_cases.accept_friend_request import AcceptFriendRequestUseCase
from ...application.use_cases.reject_friend_request import RejectFriendRequestUseCase
from ...application.use_cases.remove_friendship import RemoveFriendshipUseCase
from ...application.use_cases.get_friends import GetFriendsUseCase
from ...application.use_cases.get_friend_requests import GetFriendRequestsUseCase
from ...application.use_cases.get_friend_suggestions import GetFriendSuggestionsUseCase
from ...application.use_cases.get_friendship_stats import GetFriendshipStatsUseCase
from shared.utils.response_utils import SuccessResponse


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
        self._send_friend_request_use_case = send_friend_request_use_case
        self._accept_friend_request_use_case = accept_friend_request_use_case
        self._reject_friend_request_use_case = reject_friend_request_use_case
        self._remove_friendship_use_case = remove_friendship_use_case
        self._get_friends_use_case = get_friends_use_case
        self._get_friend_requests_use_case = get_friend_requests_use_case
        self._get_friend_suggestions_use_case = get_friend_suggestions_use_case
        self._get_friendship_stats_use_case = get_friendship_stats_use_case

    async def send_friend_request(self, dto: SendFriendRequestDTO, current_user: Dict):
        """Enviar solicitud de amistad"""
        try:
            print(f"[DEBUG] send_friend_request - dto: {dto}")
            print(f"[DEBUG] send_friend_request - friend_id: {dto.friend_id}")
            print(f"[DEBUG] send_friend_request - current_user: {current_user}")
            
            # Validación básica sin ValidationUtils
            if not dto.friend_id or len(dto.friend_id) < 10:
                raise HTTPException(status_code=400, detail="ID de usuario inválido")

            # Usar sub en lugar de id para tokens JWT
            user_id = current_user.get("sub") or current_user.get("id")
            print(f"[DEBUG] send_friend_request - user_id extracted: {user_id}")
            
            print("[DEBUG] send_friend_request - Calling use case...")
            result = await self._send_friend_request_use_case.execute(dto, user_id)
            print(f"[DEBUG] send_friend_request - Use case result: {result}")
            
            return SuccessResponse(
                data=result,
                message="Solicitud de amistad enviada exitosamente"
            )
            
        except ValueError as e:
            print(f"[ERROR] send_friend_request - ValueError: {str(e)}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            print(f"[ERROR] send_friend_request - Exception: {str(e)}")
            print(f"[ERROR] send_friend_request - Exception type: {type(e)}")
            import traceback
            print(f"[ERROR] send_friend_request - Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

    async def accept_friend_request(self, friendship_id: str, current_user: Dict):
        """Aceptar solicitud de amistad"""
        try:
            # Validación básica sin ValidationUtils
            if not friendship_id or len(friendship_id) < 10:
                raise HTTPException(status_code=400, detail="ID de solicitud inválido")

            user_id = current_user.get("sub") or current_user.get("id")
            result = await self._accept_friend_request_use_case.execute(friendship_id, user_id)
            
            return SuccessResponse(
                data=result,
                message="Solicitud de amistad aceptada exitosamente"
            )
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

    async def reject_friend_request(self, friendship_id: str, current_user: Dict):
        """Rechazar solicitud de amistad"""
        try:
            # Validación básica sin ValidationUtils
            if not friendship_id or len(friendship_id) < 10:
                raise HTTPException(status_code=400, detail="ID de solicitud inválido")

            user_id = current_user.get("sub") or current_user.get("id")
            result = await self._reject_friend_request_use_case.execute(friendship_id, user_id)
            
            return SuccessResponse(
                data=result,
                message="Solicitud de amistad rechazada exitosamente"
            )
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

    async def remove_friendship(self, friendship_id: str, current_user: Dict):
        """Eliminar amistad"""
        try:
            # Validación básica sin ValidationUtils
            if not friendship_id or len(friendship_id) < 10:
                raise HTTPException(status_code=400, detail="ID de amistad inválido")

            user_id = current_user.get("sub") or current_user.get("id")
            result = await self._remove_friendship_use_case.execute(friendship_id, user_id)
            
            return SuccessResponse(
                data=result,
                message="Amistad eliminada exitosamente"
            )
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

    async def get_friends(self, current_user: Dict, page: int = 1, limit: int = 20):
        """Obtener lista de amigos"""
        try:
            user_id = current_user.get("sub") or current_user.get("id")
            result = await self._get_friends_use_case.execute(user_id, page, limit)
            return result
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

    async def get_received_requests(self, current_user: Dict, page: int = 1, limit: int = 20):
        """Obtener solicitudes de amistad recibidas"""
        try:
            user_id = current_user.get("sub") or current_user.get("id")
            result = await self._get_friend_requests_use_case.execute_received(user_id, page, limit)
            return result
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

    async def get_sent_requests(self, current_user: Dict, page: int = 1, limit: int = 20):
        """Obtener solicitudes de amistad enviadas"""
        try:
            user_id = current_user.get("sub") or current_user.get("id")
            result = await self._get_friend_requests_use_case.execute_sent(user_id, page, limit)
            return result
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

    async def get_friend_suggestions(self, current_user: Dict, limit: int = 10):
        """Obtener sugerencias de amigos"""
        try:
            user_id = current_user.get("sub") or current_user.get("id")
            result = await self._get_friend_suggestions_use_case.execute(user_id, limit)
            
            return SuccessResponse(
                data=result,
                message="Sugerencias obtenidas exitosamente"
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

    async def get_friendship_stats(self, current_user: Dict):
        """Obtener estadísticas de amistad"""
        try:
            user_id = current_user.get("sub") or current_user.get("id")
            result = await self._get_friendship_stats_use_case.execute(user_id)
            
            return SuccessResponse(
                data=result,
                message="Estadísticas obtenidas exitosamente"
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")