# src/modules/diary_recommendations/application/dtos/diary_recommendation_dto.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from ...domain.diary_recommendation import RecommendationType


class CreateDiaryRecommendationDTO(BaseModel):
    diary_entry_id: str = Field(..., min_length=36, max_length=36)
    note: str = Field(..., min_length=3, max_length=1000)
    type: RecommendationType = Field(...)

    @validator('note')
    def validate_note(cls, v):
        if not v or not v.strip():
            raise ValueError('La nota es requerida')
        return v.strip()

    class Config:
        use_enum_values = True


class UpdateDiaryRecommendationDTO(BaseModel):
    note: Optional[str] = Field(None, min_length=3, max_length=1000)
    type: Optional[RecommendationType] = Field(None)

    @validator('note')
    def validate_note(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('La nota no puede estar vacía')
        return v.strip() if v else v

    class Config:
        use_enum_values = True


class DiaryRecommendationResponseDTO(BaseModel):
    id: str
    diary_entry_id: str
    note: str
    type: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DiaryEntryRecommendationsResponseDTO(BaseModel):
    diary_entry_id: str
    recommendations: List[DiaryRecommendationResponseDTO]
    total_count: int
    
    class Config:
        from_attributes = True