from typing import List, Optional, Dict, Any
from .diary_entry import DiaryEntry
from .interfaces.diary_entry_repository import IDiaryEntryRepository
from modules.days.domain.interfaces.day_repository import IDayRepository
from modules.trips.domain.interfaces.trip_member_repository import ITripMemberRepository
from shared.errors.custom_errors import ValidationError, NotFoundError, ForbiddenError


class DiaryEntryService:
    def __init__(
        self,
        diary_entry_repository: IDiaryEntryRepository,
        day_repository: IDayRepository,
        trip_member_repository: ITripMemberRepository
    ):
        self._diary_entry_repository = diary_entry_repository
        self._day_repository = day_repository
        self._trip_member_repository = trip_member_repository

    async def validate_entry_creation(
        self,
        day_id: str,
        user_id: str,
        content: str
    ) -> str:
        """Validar creación de entrada y retornar trip_id"""
        # Validar que el día existe
        day = await self._day_repository.find_by_id(day_id)
        if not day or not day.is_active():
            raise NotFoundError("Día no encontrado")

        # Validar permisos del usuario
        trip_id = await self._validate_user_permissions(day.trip_id, user_id, "create_diary_entry")

        # Validar que el usuario no tenga ya una entrada para este día
        existing_entry = await self._diary_entry_repository.find_by_user_and_day(user_id, day_id)
        if existing_entry and existing_entry.is_active():
            raise ValidationError("Ya tienes una entrada de diario para este día")

        # Validar contenido
        if not content or len(content.strip()) < 10:
            raise ValidationError("El contenido debe tener al menos 10 caracteres")

        return trip_id

    async def validate_entry_update(
        self,
        entry: DiaryEntry,
        user_id: str
    ) -> str:
        """Validar actualización de entrada y retornar trip_id"""
        if not entry.is_active():
            raise ValidationError("No se puede actualizar una entrada eliminada")

        if not entry.can_be_edited_by(user_id):
            raise ForbiddenError("No tienes permisos para editar esta entrada")

        day = await self._day_repository.find_by_id(entry.day_id)
        if not day or not day.is_active():
            raise NotFoundError("Día no encontrado")

        trip_id = await self._validate_user_permissions(day.trip_id, user_id, "edit_diary_entry")
        return trip_id

    async def validate_entry_deletion(
        self,
        entry: DiaryEntry,
        user_id: str
    ) -> str:
        """Validar eliminación de entrada y retornar trip_id"""
        if not entry.is_active():
            raise ValidationError("La entrada ya está eliminada")

        if not entry.can_be_edited_by(user_id):
            raise ForbiddenError("No tienes permisos para eliminar esta entrada")

        day = await self._day_repository.find_by_id(entry.day_id)
        if not day or not day.is_active():
            raise NotFoundError("Día no encontrado")

        trip_id = await self._validate_user_permissions(day.trip_id, user_id, "delete_diary_entry")
        return trip_id

    async def validate_user_can_view_entry(
        self,
        entry: DiaryEntry,
        user_id: str
    ) -> bool:
        """Validar si el usuario puede ver la entrada"""
        if not entry.is_active():
            return False

        day = await self._day_repository.find_by_id(entry.day_id)
        if not day or not day.is_active():
            return False

        try:
            member = await self._trip_member_repository.find_by_trip_and_user(day.trip_id, user_id)
            return member is not None
        except:
            return False

    async def validate_user_can_view_day_entries(
        self,
        day_id: str,
        user_id: str
    ) -> bool:
        """Validar si el usuario puede ver entradas del día"""
        day = await self._day_repository.find_by_id(day_id)
        if not day or not day.is_active():
            return False

        try:
            member = await self._trip_member_repository.find_by_trip_and_user(day.trip_id, user_id)
            return member is not None
        except:
            return False

    async def get_day_diary_statistics(
        self,
        day_id: str
    ) -> Dict[str, Any]:
        """Obtener estadísticas de entradas del día"""
        entries = await self._diary_entry_repository.find_by_day_id(day_id)
        
        total_entries = len(entries)
        total_words = sum(entry.get_word_count() for entry in entries)
        entries_with_emotions = len([e for e in entries if e.emotions])

        # Análisis de emociones
        emotion_counts = {}
        for entry in entries:
            if entry.emotions and "emotions" in entry.emotions:
                for emotion in entry.emotions["emotions"]:
                    emotion_type = emotion.get("type")
                    if emotion_type:
                        emotion_counts[emotion_type] = emotion_counts.get(emotion_type, 0) + 1

        return {
            "total_entries": total_entries,
            "total_words": total_words,
            "entries_with_emotions": entries_with_emotions,
            "emotion_distribution": emotion_counts,
            "average_words_per_entry": total_words / total_entries if total_entries > 0 else 0
        }

    async def get_trip_diary_summary(
        self,
        trip_id: str
    ) -> Dict[str, Any]:
        """Obtener resumen del diario del viaje"""
        entries = await self._diary_entry_repository.find_by_trip_id(trip_id)
        
        total_entries = len(entries)
        total_words = sum(entry.get_word_count() for entry in entries)

        # Análisis por usuario
        user_stats = {}
        for entry in entries:
            user_id = entry.user_id
            if user_id not in user_stats:
                user_stats[user_id] = {"entries": 0, "words": 0}
            user_stats[user_id]["entries"] += 1
            user_stats[user_id]["words"] += entry.get_word_count()

        # Análisis de emociones generales
        emotion_trends = await self._diary_entry_repository.get_emotion_trends(trip_id)

        return {
            "total_entries": total_entries,
            "total_words": total_words,
            "user_contributions": user_stats,
            "emotion_trends": emotion_trends,
            "average_words_per_entry": total_words / total_entries if total_entries > 0 else 0
        }

    async def suggest_emotions_for_content(
        self,
        content: str
    ) -> List[str]:
        """Sugerir emociones basadas en el contenido (análisis básico)"""
        content_lower = content.lower()
        suggested_emotions = []

        # Palabras clave para diferentes emociones
        emotion_keywords = {
            "happy": ["feliz", "contento", "alegre", "genial", "increíble", "perfecto", "excelente"],
            "excited": ["emocionado", "emocionante", "expectativa", "ansioso", "nervioso"],
            "relaxed": ["relajado", "tranquilo", "paz", "calma", "sereno"],
            "adventurous": ["aventura", "explorar", "descubrir", "adrenalina", "extremo"],
            "nostalgic": ["recuerdo", "nostalgia", "extraño", "melancolía", "añoro"],
            "tired": ["cansado", "agotado", "exhausto", "fatiga"],
            "sad": ["triste", "decepcionado", "mal", "horrible", "terrible"]
        }

        for emotion, keywords in emotion_keywords.items():
            if any(keyword in content_lower for keyword in keywords):
                suggested_emotions.append(emotion)

        return suggested_emotions[:3]  # Máximo 3 sugerencias

    async def _validate_user_permissions(
        self,
        trip_id: str,
        user_id: str,
        action: str
    ) -> str:
        """Validar permisos del usuario para la acción especificada"""
        member = await self._trip_member_repository.find_by_trip_and_user(trip_id, user_id)
        if not member:
            raise ForbiddenError("No eres miembro de este viaje")

        # Todos los miembros pueden crear/editar/eliminar sus propias entradas
        if action in ["create_diary_entry", "edit_diary_entry", "delete_diary_entry"]:
            return trip_id

        raise ForbiddenError(f"No tienes permisos para: {action}")