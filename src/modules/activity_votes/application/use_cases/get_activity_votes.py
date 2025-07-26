# src/modules/activity_votes/application/use_cases/get_activity_votes.py
from ..dtos.activity_vote_dto import ActivityVoteStatsDTO, ActivityVoteDTOMapper
from ...domain.activity_vote_service import ActivityVoteService


class GetActivityVotesUseCase:
    def __init__(self, activity_vote_service: ActivityVoteService):
        self._activity_vote_service = activity_vote_service

    async def execute(self, activity_id: str, user_id: str) -> ActivityVoteStatsDTO:
        """Obtener estadísticas de votos de una actividad"""
        # Verificar que el usuario puede acceder a la actividad
        can_access = await self._activity_vote_service.can_user_vote_activity(
            activity_id, user_id
        )
        if not can_access:
            from shared.errors.custom_errors import ForbiddenError
            raise ForbiddenError("No tienes acceso a esta actividad")

        # Obtener estadísticas de votos
        stats = await self._activity_vote_service.get_activity_vote_summary(activity_id)
        
        # Obtener el voto del usuario actual
        user_vote = await self._activity_vote_service.get_user_vote_for_activity(
            activity_id, user_id
        )

        return ActivityVoteDTOMapper.to_activity_vote_stats(stats, user_vote)