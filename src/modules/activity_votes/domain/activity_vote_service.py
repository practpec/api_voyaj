# src/modules/activity_votes/domain/activity_vote_service.py
from typing import Dict, Any, List, Optional
from .interfaces.activity_vote_repository import IActivityVoteRepository
from modules.activities.domain.interfaces.activity_repository import IActivityRepository
from modules.trips.domain.interfaces.trip_member_repository import ITripMemberRepository
from shared.errors.custom_errors import NotFoundError, ForbiddenError, ValidationError


class ActivityVoteService:
    """Servicio de dominio para gestión de votos de actividades"""

    def __init__(
        self,
        activity_vote_repository: IActivityVoteRepository,
        activity_repository: IActivityRepository,
        trip_member_repository: ITripMemberRepository
    ):
        self._activity_vote_repository = activity_vote_repository
        self._activity_repository = activity_repository
        self._trip_member_repository = trip_member_repository

    async def validate_vote_creation(
        self, 
        activity_id: str, 
        user_id: str
    ) -> str:
        """Validar que se pueda crear un voto"""
        # Verificar que la actividad existe
        activity = await self._activity_repository.find_by_id(activity_id)
        if not activity or not activity.is_active():
            raise NotFoundError("Actividad no encontrada")

        # Verificar que el usuario es miembro del viaje
        member = await self._trip_member_repository.find_by_trip_and_user(
            activity.trip_id, user_id
        )
        if not member or not member.is_active():
            raise ForbiddenError("No tienes acceso a este viaje")

        return activity.trip_id

    async def can_user_vote_activity(self, activity_id: str, user_id: str) -> bool:
        """Verificar si el usuario puede votar la actividad"""
        try:
            await self.validate_vote_creation(activity_id, user_id)
            return True
        except (NotFoundError, ForbiddenError):
            return False

    async def get_user_vote_for_activity(
        self, 
        activity_id: str, 
        user_id: str
    ) -> Optional[str]:
        """Obtener el voto del usuario para una actividad"""
        vote = await self._activity_vote_repository.find_by_activity_and_user(
            activity_id, user_id
        )
        return vote.vote_type if vote and vote.is_active() else None

    async def calculate_activity_score(self, activity_id: str) -> int:
        """Calcular puntuación de la actividad (up votes - down votes)"""
        stats = await self._activity_vote_repository.get_activity_vote_stats(activity_id)
        up_votes = stats.get('up', 0)
        down_votes = stats.get('down', 0)
        return up_votes - down_votes

    async def get_activity_vote_summary(self, activity_id: str) -> Dict[str, Any]:
        """Obtener resumen completo de votos de una actividad"""
        stats = await self._activity_vote_repository.get_activity_vote_stats(activity_id)
        total_votes = sum(stats.values())
        score = stats.get('up', 0) - stats.get('down', 0)
        
        return {
            'activity_id': activity_id,
            'total_votes': total_votes,
            'up_votes': stats.get('up', 0),
            'down_votes': stats.get('down', 0),
            'neutral_votes': stats.get('neutral', 0),
            'score': score,
            'popularity_percentage': round((stats.get('up', 0) / total_votes * 100) if total_votes > 0 else 0, 1)
        }

    async def get_trip_activity_rankings(self, trip_id: str, user_id: str) -> List[Dict[str, Any]]:
        """Obtener ranking de actividades del viaje por votos"""
        # Verificar acceso al viaje
        member = await self._trip_member_repository.find_by_trip_and_user(trip_id, user_id)
        if not member or not member.is_active():
            raise ForbiddenError("No tienes acceso a este viaje")

        return await self._activity_vote_repository.get_trip_vote_rankings(trip_id)

    async def get_trip_polls(self, trip_id: str, user_id: str) -> List[Dict[str, Any]]:
        """Obtener encuestas activas del viaje"""
        # Verificar acceso al viaje
        member = await self._trip_member_repository.find_by_trip_and_user(trip_id, user_id)
        if not member or not member.is_active():
            raise ForbiddenError("No tienes acceso a este viaje")

        return await self._activity_vote_repository.get_trip_polls(trip_id)

    async def validate_vote_change(
        self, 
        vote_id: str, 
        user_id: str, 
        new_vote_type: str
    ) -> None:
        """Validar cambio de voto"""
        vote = await self._activity_vote_repository.find_by_id(vote_id)
        if not vote or not vote.is_active():
            raise NotFoundError("Voto no encontrado")

        if vote.user_id != user_id:
            raise ForbiddenError("Solo puedes modificar tus propios votos")

        if new_vote_type not in ['up', 'down', 'neutral']:
            raise ValidationError("Tipo de voto inválido")

    async def validate_vote_deletion(self, vote_id: str, user_id: str) -> None:
        """Validar eliminación de voto"""
        vote = await self._activity_vote_repository.find_by_id(vote_id)
        if not vote or not vote.is_active():
            raise NotFoundError("Voto no encontrado")

        if vote.user_id != user_id:
            raise ForbiddenError("Solo puedes eliminar tus propios votos")