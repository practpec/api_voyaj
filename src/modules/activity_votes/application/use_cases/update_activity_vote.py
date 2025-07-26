# src/modules/activity_votes/application/use_cases/update_activity_vote.py
from ..dtos.activity_vote_dto import UpdateActivityVoteDTO, ActivityVoteResponseDTO, ActivityVoteDTOMapper
from ...domain.activity_vote_service import ActivityVoteService
from ...domain.interfaces.activity_vote_repository import IActivityVoteRepository


class UpdateActivityVoteUseCase:
    def __init__(
        self,
        activity_vote_repository: IActivityVoteRepository,
        activity_vote_service: ActivityVoteService
    ):
        self._activity_vote_repository = activity_vote_repository
        self._activity_vote_service = activity_vote_service

    async def execute(
        self, 
        activity_id: str, 
        dto: UpdateActivityVoteDTO, 
        user_id: str
    ) -> ActivityVoteResponseDTO:
        """Actualizar voto de actividad del usuario"""
        # Buscar voto existente del usuario para esta actividad
        existing_vote = await self._activity_vote_repository.find_by_activity_and_user(
            activity_id, user_id
        )
        
        if not existing_vote or not existing_vote.is_active():
            from shared.errors.custom_errors import NotFoundError
            raise NotFoundError("No tienes un voto registrado para esta actividad")

        # Validar el cambio de voto
        await self._activity_vote_service.validate_vote_change(
            existing_vote.id, user_id, dto.vote_type
        )

        # Actualizar el voto
        existing_vote.change_vote_type(dto.vote_type)
        
        # Guardar cambios
        updated_vote = await self._activity_vote_repository.update(existing_vote)

        return ActivityVoteDTOMapper.to_activity_vote_response(
            updated_vote.to_public_data()
        )