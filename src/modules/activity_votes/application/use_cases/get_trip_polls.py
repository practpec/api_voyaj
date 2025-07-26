# src/modules/activity_votes/application/use_cases/get_trip_polls.py
from ..dtos.activity_vote_dto import TripPollsResponseDTO
from ...domain.activity_vote_service import ActivityVoteService


class GetTripPollsUseCase:
    def __init__(self, activity_vote_service: ActivityVoteService):
        self._activity_vote_service = activity_vote_service

    async def execute(self, trip_id: str, user_id: str) -> TripPollsResponseDTO:
        """Obtener encuestas activas del viaje"""
        polls_data = await self._activity_vote_service.get_trip_polls(trip_id, user_id)

        return TripPollsResponseDTO(
            trip_id=trip_id,
            active_polls=len(polls_data),
            polls=polls_data
        )