# src/modules/activity_votes/application/use_cases/create_activity_vote.py
from ..dtos.activity_vote_dto import CreateActivityVoteDTO, ActivityVoteResponseDTO, ActivityVoteDTOMapper
from ...domain.activity_vote import ActivityVote
from ...domain.activity_vote_service import ActivityVoteService
from ...domain.interfaces.activity_vote_repository import IActivityVoteRepository
from shared.errors.custom_errors import ValidationError


class CreateActivityVoteUseCase:
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
        dto: CreateActivityVoteDTO, 
        user_id: str
    ) -> ActivityVoteResponseDTO:
        """Crear voto para una actividad"""
        # Validar que se puede crear el voto
        trip_id = await self._activity_vote_service.validate_vote_creation(
            activity_id, user_id
        )

        # Verificar si ya existe un voto del usuario para esta actividad
        existing_vote = await self._activity_vote_repository.find_by_activity_and_user(
            activity_id, user_id
        )
        
        if existing_vote and existing_vote.is_active():
            raise ValidationError("Ya tienes un voto registrado para esta actividad")

        # Crear nuevo voto
        activity_vote = ActivityVote.create(
            activity_id=activity_id,
            user_id=user_id,
            trip_id=trip_id,
            vote_type=dto.vote_type
        )

        # Guardar en base de datos
        created_vote = await self._activity_vote_repository.create(activity_vote)

        return ActivityVoteDTOMapper.to_activity_vote_response(
            created_vote.to_public_data()
        )