# Reemplazar el contenido completo de trip_export_service.py

import os
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
import pandas as pd

from ...domain.trip import Trip
from ...domain.trip_member import TripMember
from ...application.dtos.trip_invitation_dto import ExportTripResponseDTO


class TripExportService:
    def __init__(self, export_dir: str = "exports"):
        self.export_dir = Path(export_dir)
        self.base_url = os.getenv("BASE_URL", "http://localhost:8000")
        self._ensure_export_directory()

    def _ensure_export_directory(self):
        self.export_dir.mkdir(parents=True, exist_ok=True)

    async def export_trip_to_excel(
        self,
        trip: Trip,
        members: List[TripMember],
        user_data: Dict[str, Any]
    ) -> ExportTripResponseDTO:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"trip_{trip.id}_{timestamp}.xlsx"
        file_path = self.export_dir / file_name

        trip_data = {
            "ID": [trip.id],
            "Título": [trip.title],
            "Descripción": [trip.description or ""],
            "Destino": [trip.destination],
            "Fecha Inicio": [trip.start_date.strftime("%Y-%m-%d")],
            "Fecha Fin": [trip.end_date.strftime("%Y-%m-%d")],
            "Categoría": [trip.category],
            "Estado": [trip.status],
            "Es Viaje Grupal": [trip.is_group_trip],
            "Es Público": [trip.is_public],
            "Presupuesto": [trip.budget_limit or 0],
            "Moneda": [trip.currency],
            "Gastos Totales": [trip.total_expenses],
            "Cantidad Miembros": [trip.member_count],
            "Creado": [trip.created_at.strftime("%Y-%m-%d %H:%M:%S")],
            "Actualizado": [trip.updated_at.strftime("%Y-%m-%d %H:%M:%S")]
        }

        members_data = []
        for member in members:
            member_user = user_data.get(member.user_id, {})
            members_data.append({
                "ID": member.id,
                "Usuario": member_user.get("name", "Usuario desconocido"),
                "Email": member_user.get("email", ""),
                "Rol": member.role,
                "Estado": member.status,
                "Invitado": member.invited_at.strftime("%Y-%m-%d %H:%M:%S"),
                "Se Unió": member.joined_at.strftime("%Y-%m-%d %H:%M:%S") if member.joined_at else "",
                "Notas": member.notes or ""
            })

        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            pd.DataFrame(trip_data).to_excel(writer, sheet_name="Información del Viaje", index=False)
            
            if members_data:
                pd.DataFrame(members_data).to_excel(writer, sheet_name="Miembros", index=False)

        file_size = file_path.stat().st_size

        return ExportTripResponseDTO(
            file_name=file_name,
            file_url=f"{self.base_url}/exports/{file_name}",
            file_size=file_size,
            format="excel",
            generated_at=datetime.utcnow()
        )

    async def export_trip_to_csv(
        self,
        trip: Trip,
        members: List[TripMember],
        user_data: Dict[str, Any]
    ) -> ExportTripResponseDTO:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"trip_{trip.id}_{timestamp}.csv"
        file_path = self.export_dir / file_name

        data = []
        for member in members:
            member_user = user_data.get(member.user_id, {})
            data.append({
                "trip_id": trip.id,
                "trip_title": trip.title,
                "trip_destination": trip.destination,
                "trip_start_date": trip.start_date.strftime("%Y-%m-%d"),
                "trip_end_date": trip.end_date.strftime("%Y-%m-%d"),
                "trip_category": trip.category,
                "trip_status": trip.status,
                "member_name": member_user.get("name", "Usuario desconocido"),
                "member_email": member_user.get("email", ""),
                "member_role": member.role,
                "member_status": member.status,
                "member_joined_at": member.joined_at.strftime("%Y-%m-%d %H:%M:%S") if member.joined_at else "",
                "member_notes": member.notes or ""
            })

        df = pd.DataFrame(data)
        df.to_csv(file_path, index=False, encoding='utf-8')

        file_size = file_path.stat().st_size

        return ExportTripResponseDTO(
            file_name=file_name,
            file_url=f"{self.base_url}/exports/{file_name}",
            file_size=file_size,
            format="csv",
            generated_at=datetime.utcnow()
        )

    async def cleanup_old_exports(self, older_than_hours: int = 24) -> int:
        cutoff_time = datetime.now().timestamp() - (older_than_hours * 3600)
        deleted_count = 0

        try:
            for file_path in self.export_dir.iterdir():
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    deleted_count += 1
        except Exception as e:
            print(f"Error al limpiar archivos de exportación: {e}")

        return deleted_count