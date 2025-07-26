from typing import List
from ..dtos.trip_dto import TripFiltersDTO, TripListResponseDTO, TripDTOMapper
from ...domain.interfaces.trip_repository import ITripRepository
from ...domain.interfaces.trip_member_repository import ITripMemberRepository
from ...domain.trip_service import TripService
from shared.utils.pagination_utils import PaginatedResponse


class GetUserTripsUseCase:
    def __init__(
        self,
        trip_repository: ITripRepository,
        trip_member_repository: ITripMemberRepository,
        trip_service: TripService
    ):
        self._trip_repository = trip_repository
        self._trip_member_repository = trip_member_repository
        self._trip_service = trip_service

    async def execute(
        self,
        user_id: str,
        filters: TripFiltersDTO
    ) -> PaginatedResponse[TripListResponseDTO]:
        page = (filters.offset // filters.limit) + 1

        filter_dict = {
            "owner_id": user_id,
            "status": filters.status,
            "category": filters.category,
            "is_group_trip": filters.is_group_trip,
            "destination": filters.destination,
            "start_date": filters.start_date,
            "end_date": filters.end_date,
            "is_active": filters.is_active
        }

        filter_dict = {k: v for k, v in filter_dict.items() if v is not None}

        trips, total = await self._trip_repository.find_with_filters(
            filter_dict, 
            page, 
            filters.limit
        )

        if not trips:
            return PaginatedResponse(
                data=[],
                total=0,
                page=page,
                limit=filters.limit,
                total_pages=0
            )

        trip_responses: List[TripListResponseDTO] = []
        
        for trip in trips:
            user_role = await self._trip_service.get_user_role_in_trip(trip.id, user_id)
            
            trip_response = TripDTOMapper.to_trip_list_response(
                trip.to_public_data(),
                user_role
            )
            trip_responses.append(trip_response)

        total_pages = (total + filters.limit - 1) // filters.limit

        return PaginatedResponse(
            data=trip_responses,
            total=total,
            page=page,
            limit=filters.limit,
            total_pages=total_pages
        )