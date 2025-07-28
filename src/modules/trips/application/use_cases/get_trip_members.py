from typing import List
from ..dtos.trip_member_dto import TripMemberFiltersDTO, TripMemberListResponseDTO, TripMemberDTOMapper
from ...domain.trip_service import TripService
from ...domain.interfaces.trip_repository import ITripRepository
from ...domain.interfaces.trip_member_repository import ITripMemberRepository
from modules.users.domain.interfaces.IUserRepository import IUserRepository
from shared.utils.pagination_utils import PaginatedResponse
from shared.errors.custom_errors import NotFoundError, ForbiddenError


class GetTripMembersUseCase:
    def __init__(
        self,
        trip_member_repository: ITripMemberRepository,
        user_repository: IUserRepository,
        trip_service: TripService
    ):
        self._trip_member_repository = trip_member_repository
        self._user_repository = user_repository
        self._trip_service = trip_service

    async def execute(
        self,
        trip_id: str,
        user_id: str,
        filters: TripMemberFiltersDTO
    ) -> PaginatedResponse[TripMemberListResponseDTO]:
        page = (filters.offset // filters.limit) + 1

        members, total = await self._trip_member_repository.find_by_trip_id(
            trip_id, page, filters.limit
        )

        if not members:
            return PaginatedResponse(
                data=[],
                total=0,
                page=page,
                limit=filters.limit,
                total_pages=0
            )

        user_member = await self._trip_member_repository.find_by_trip_and_user(trip_id, user_id)
        can_edit_members = user_member.can_edit_trip() if user_member else False

        member_responses: List[TripMemberListResponseDTO] = []
        
        for member in members:
            user_info = await self._user_repository.find_by_id(member.user_id)
            if not user_info:
                continue

            can_remove = can_edit_members and not member.is_owner()

            member_response = TripMemberDTOMapper.to_member_list_response(
                member.to_public_data(),
                user_info.to_public_dict(),
                can_edit_members,
                can_remove
            )
            
            member_responses.append(member_response)

        total_pages = (total + filters.limit - 1) // filters.limit

        return PaginatedResponse(
            data=member_responses,
            total=total,
            page=page,
            limit=filters.limit,
            total_pages=total_pages
        )