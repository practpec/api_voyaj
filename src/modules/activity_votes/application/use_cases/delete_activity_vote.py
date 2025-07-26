# src/modules/activity_votes/application/use_cases/delete_activity_vote.py
from ...domain.activity_vote_service import ActivityVoteService
from ...domain.interfaces.activity_vote_repository import IActivityVoteRepository


class DeleteActivityVoteUseCase:
    def __init__(
        self,
        activity_vote_repository: IActivityVoteRepository,
        activity_vote_service: ActivityVoteService
    ):
        self._activity_vote_repository = activity_vote_repository
        self._activity_vote_service = activity_vote_service

    async def execute(self, activity_id: str, user_id: str) -> dict:
        """Eliminar voto de actividad del usuario"""
        # Buscar voto existente del usuario para esta actividad
        existing_vote = await self._activity_vote_repository.find_by_activity_and_user(
            activity_id, user_id
        )
        
        if not existing_vote or not existing_vote.is_active():
            from shared.errors.custom_errors import NotFoundError
            raise NotFoundError("No tienes un voto registrado para esta actividad")

        # Validar la eliminación
        await self._activity_vote_service.validate_vote_deletion(
            existing_vote.id, user_id
        )

        # Eliminar el voto (soft delete)
        await self._activity_vote_repository.delete(existing_vote.id)

        return {"message": "Voto eliminado exitosamente"}