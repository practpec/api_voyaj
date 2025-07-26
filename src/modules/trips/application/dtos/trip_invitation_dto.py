from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any
from ...domain.trip_member import TripMemberData, TripMemberRole


@dataclass
class SendTripInvitationDTO:
    email: str
    role: TripMemberRole = TripMemberRole.MEMBER
    message: Optional[str] = None


@dataclass
class BulkInviteMembersDTO:
    invitations: List[SendTripInvitationDTO]


@dataclass
class ResendInvitationDTO:
    member_id: str
    message: Optional[str] = None


@dataclass
class TripInvitationResponseDTO:
    id: str
    trip_id: str
    trip_title: str
    trip_destination: str
    invited_user_email: str
    invited_user_name: Optional[str]
    inviter_name: str
    role: str
    status: str
    invited_at: datetime
    message: Optional[str]
    trip_start_date: datetime
    trip_end_date: datetime


@dataclass
class PendingInvitationsResponseDTO:
    id: str
    trip_info: Dict[str, Any]
    inviter_info: Dict[str, Any]
    role: str
    invited_at: datetime
    message: Optional[str]
    days_pending: int


@dataclass
class SentInvitationsResponseDTO:
    id: str
    invited_user_email: str
    invited_user_name: Optional[str]
    role: str
    status: str
    invited_at: datetime
    response_at: Optional[datetime]
    days_since_sent: int


@dataclass
class ExportTripDTO:
    format: str = "excel"  # "excel", "pdf", "csv"
    include_members: bool = True
    include_activities: bool = False
    include_expenses: bool = False


@dataclass
class ExportTripResponseDTO:
    file_name: str
    file_url: str
    file_size: int
    format: str
    generated_at: datetime


class TripInvitationDTOMapper:
    
    @staticmethod
    def to_invitation_response(
        member: TripMemberData,
        trip_info: Dict[str, Any],
        inviter_info: Dict[str, Any],
        invited_user_info: Optional[Dict[str, Any]] = None
    ) -> TripInvitationResponseDTO:
        return TripInvitationResponseDTO(
            id=member.id,
            trip_id=member.trip_id,
            trip_title=trip_info.get("title", ""),
            trip_destination=trip_info.get("destination", ""),
            invited_user_email=invited_user_info.get("email", "") if invited_user_info else "",
            invited_user_name=invited_user_info.get("name", "") if invited_user_info else None,
            inviter_name=inviter_info.get("name", ""),
            role=member.role,
            status=member.status,
            invited_at=member.invited_at,
            message=member.notes,
            trip_start_date=trip_info.get("start_date"),
            trip_end_date=trip_info.get("end_date")
        )

    @staticmethod
    def to_pending_invitation_response(
        member: TripMemberData,
        trip_info: Dict[str, Any],
        inviter_info: Dict[str, Any]
    ) -> PendingInvitationsResponseDTO:
        days_pending = (datetime.utcnow() - member.invited_at).days
        
        return PendingInvitationsResponseDTO(
            id=member.id,
            trip_info=trip_info,
            inviter_info=inviter_info,
            role=member.role,
            invited_at=member.invited_at,
            message=member.notes,
            days_pending=days_pending
        )

    @staticmethod
    def to_sent_invitation_response(
        member: TripMemberData,
        invited_user_info: Dict[str, Any]
    ) -> SentInvitationsResponseDTO:
        days_since_sent = (datetime.utcnow() - member.invited_at).days
        response_at = member.joined_at if member.status == "accepted" else None
        
        return SentInvitationsResponseDTO(
            id=member.id,
            invited_user_email=invited_user_info.get("email", ""),
            invited_user_name=invited_user_info.get("name"),
            role=member.role,
            status=member.status,
            invited_at=member.invited_at,
            response_at=response_at,
            days_since_sent=days_since_sent
        )