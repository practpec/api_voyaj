# src/modules/activity_votes/infrastructure/controllers/activity_vote_controller.py
from fastapi import APIRouter, HTTPException
from typing import Annotated

from ...application.dtos.activity_vote_dto import (
    CreateActivityVoteDTO, UpdateActivityVoteDTO,
    ActivityVoteResponseDTO, ActivityVoteStatsDTO,
    TripRankingsResponseDTO, TripPollsResponseDTO
)
from ...application.use_cases.create_activity_vote import CreateActivityVoteUseCase
from ...application.use_cases.get_activity_votes import GetActivityVotesUseCase
from ...application.use_cases.update_activity_vote import UpdateActivityVoteUseCase
from ...application.use_cases.delete_activity_vote import DeleteActivityVoteUseCase
from ...application.use_cases.get_trip_rankings import GetTripRankingsUseCase
from ...application.use_cases.get_trip_polls import GetTripPollsUseCase

from shared.utils.response_utils import SuccessResponse
from shared.errors.custom_errors import NotFoundError, ForbiddenError, ValidationError


class ActivityVoteController:
    def __init__(
        self,
        create_activity_vote_use_case: CreateActivityVoteUseCase,
        get_activity_votes_use_case: GetActivityVotesUseCase,
        update_activity_vote_use_case: UpdateActivityVoteUseCase,
        delete_activity_vote_use_case: DeleteActivityVoteUseCase,
        get_trip_rankings_use_case: GetTripRankingsUseCase,
        get_trip_polls_use_case: GetTripPollsUseCase
    ):
        self.router = APIRouter(prefix="/api/activities", tags=["votos de actividades"])
        self._create_activity_vote_use_case = create_activity_vote_use_case
        self._get_activity_votes_use_case = get_activity_votes_use_case
        self._update_activity_vote_use_case = update_activity_vote_use_case
        self._delete_activity_vote_use_case = delete_activity_vote_use_case
        self._get_trip_rankings_use_case = get_trip_rankings_use_case
        self._get_trip_polls_use_case = get_trip_polls_use_case

    async def vote_activity(
        self, 
        activity_id: str, 
        dto: CreateActivityVoteDTO, 
        current_user: dict
    ) -> SuccessResponse:
        """Votar una actividad"""
        try:
            result = await self._create_activity_vote_use_case.execute(
                activity_id, dto, current_user["id"]
            )
            return SuccessResponse(
                message="Voto registrado exitosamente",
                data=result
            )
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except ForbiddenError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    async def get_activity_votes(
        self, 
        activity_id: str, 
        current_user: dict
    ) -> SuccessResponse:
        """Obtener estadísticas de votos de una actividad"""
        try:
            result = await self._get_activity_votes_use_case.execute(
                activity_id, current_user["id"]
            )
            return SuccessResponse(
                message="Estadísticas de votos obtenidas exitosamente",
                data=result
            )
        except ForbiddenError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    async def update_activity_vote(
        self, 
        activity_id: str, 
        dto: UpdateActivityVoteDTO, 
        current_user: dict
    ) -> SuccessResponse:
        """Actualizar voto de actividad"""
        try:
            result = await self._update_activity_vote_use_case.execute(
                activity_id, dto, current_user["id"]
            )
            return SuccessResponse(
                message="Voto actualizado exitosamente",
                data=result
            )
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except ForbiddenError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    async def delete_activity_vote(
        self, 
        activity_id: str, 
        current_user: dict
    ) -> SuccessResponse:
        """Eliminar voto de actividad"""
        try:
            result = await self._delete_activity_vote_use_case.execute(
                activity_id, current_user["id"]
            )
            return SuccessResponse(
                message="Voto eliminado exitosamente",
                data=result
            )
        except ForbiddenError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    async def get_trip_rankings(
        self, 
        trip_id: str, 
        current_user: dict
    ) -> SuccessResponse:
        """Obtener ranking de actividades del viaje"""
        try:
            result = await self._get_trip_rankings_use_case.execute(
                trip_id, current_user["id"]
            )
            return SuccessResponse(
                message="Ranking obtenido exitosamente",
                data=result
            )
        except ForbiddenError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    async def get_trip_polls(
        self, 
        trip_id: str, 
        current_user: dict
    ) -> SuccessResponse:
        """Obtener encuestas activas del viaje"""
        try:
            result = await self._get_trip_polls_use_case.execute(
                trip_id, current_user["id"]
            )
            return SuccessResponse(
                message="Encuestas obtenidas exitosamente",
                data=result
            )
        except ForbiddenError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    async def health_check(self) -> SuccessResponse:
        """Health check del módulo"""
        return SuccessResponse(
            message="Módulo activity_votes funcionando correctamente",
            data={"status": "healthy", "module": "activity_votes"}
        )