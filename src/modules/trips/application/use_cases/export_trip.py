from ..dtos.trip_invitation_dto import ExportTripDTO, ExportTripResponseDTO
from ...domain.interfaces.trip_repository import ITripRepository
from ...domain.interfaces.trip_member_repository import ITripMemberRepository
from modules.users.domain.interfaces.IUserRepository import IUserRepository
from ...infrastructure.services.trip_export_service import TripExportService
from shared.errors.custom_errors import NotFoundError, ForbiddenError


class ExportTripUseCase:
    def __init__(
        self,
        trip_repository: ITripRepository,
        trip_member_repository: ITripMemberRepository,
        user_repository: IUserRepository,
        export_service: TripExportService
    ):
        self._trip_repository = trip_repository
        self._trip_member_repository = trip_member_repository
        self._user_repository = user_repository
        self._export_service = export_service

    async def execute(
        self, 
        trip_id: str, 
        dto: ExportTripDTO, 
        user_id: str
    ) -> ExportTripResponseDTO:
        trip = await self._trip_repository.find_by_id(trip_id)
        if not trip or not trip.is_active():
            raise NotFoundError("Viaje no encontrado")

        member = await self._trip_member_repository.find_by_trip_and_user(trip_id, user_id)
        if not member or not member.can_edit_trip():
            raise ForbiddenError("No tienes permisos para exportar este viaje")

        members = []
        user_data = {}
        
        if dto.include_members:
            members = await self._trip_member_repository.find_active_members_by_trip_id(trip_id)
            
            for member in members:
                user_info = await self._user_repository.find_by_id(member.user_id)
                if user_info:
                    user_data[member.user_id] = user_info.to_public_data()

        if dto.format == "excel":
            return await self._export_service.export_trip_to_excel(trip, members, user_data)
        elif dto.format == "csv":
            return await self._export_service.export_trip_to_csv(trip, members, user_data)
        else:
            raise ValueError("Formato de exportación no soportado. Use 'excel' o 'csv'")