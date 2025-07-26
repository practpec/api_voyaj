import cloudinary
import cloudinary.uploader
import os
from typing import Dict, Any, Optional
from fastapi import UploadFile
from ..exceptions.UploadExceptions import (
    FileTooLargeException, 
    InvalidFileTypeException, 
    UploadFailedException,
    CloudinaryException
)

class UploadService:
    def __init__(self):
        cloudinary.config(
            cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
            api_key=os.getenv("CLOUDINARY_API_KEY"),
            api_secret=os.getenv("CLOUDINARY_API_SECRET")
        )
        
        self.max_file_size = 5 * 1024 * 1024  # 5MB
        self.allowed_image_types = {
            "image/jpeg", "image/jpg", "image/png", "image/webp", "image/gif"
        }
        self.allowed_document_types = {
            "application/pdf", "text/plain", "application/msword",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        }

    async def upload_profile_picture(self, file: UploadFile, user_id: str) -> Dict[str, str]:
        """Subir imagen de perfil de usuario"""
        self._validate_image_file(file)
        
        try:
            file_content = await file.read()
            
            result = cloudinary.uploader.upload(
                file_content,
                folder=f"voyaj/profiles/{user_id}",
                transformation=[
                    {"width": 400, "height": 400, "crop": "fill", "gravity": "face"},
                    {"quality": "auto", "fetch_format": "auto"}
                ],
                public_id=f"profile_{user_id}",
                overwrite=True
            )
            
            return {
                "url": result["secure_url"],
                "public_id": result["public_id"]
            }
            
        except Exception as e:
            raise CloudinaryException(f"Error subiendo imagen de perfil: {str(e)}")

    async def upload_trip_photo(self, file: UploadFile, trip_id: str, user_id: str) -> Dict[str, str]:
        """Subir foto de viaje"""
        self._validate_image_file(file)
        
        try:
            file_content = await file.read()
            
            result = cloudinary.uploader.upload(
                file_content,
                folder=f"voyaj/trips/{trip_id}/photos",
                transformation=[
                    {"width": 1200, "height": 800, "crop": "limit"},
                    {"quality": "auto", "fetch_format": "auto"}
                ],
                context=f"trip_id={trip_id}|user_id={user_id}"
            )
            
            return {
                "url": result["secure_url"],
                "public_id": result["public_id"]
            }
            
        except Exception as e:
            raise CloudinaryException(f"Error subiendo foto de viaje: {str(e)}")

    async def upload_document(self, file: UploadFile, folder: str, user_id: str) -> Dict[str, str]:
        """Subir documento"""
        self._validate_document_file(file)
        
        try:
            file_content = await file.read()
            
            result = cloudinary.uploader.upload(
                file_content,
                folder=f"voyaj/{folder}/{user_id}",
                resource_type="raw",
                context=f"user_id={user_id}"
            )
            
            return {
                "url": result["secure_url"],
                "public_id": result["public_id"]
            }
            
        except Exception as e:
            raise CloudinaryException(f"Error subiendo documento: {str(e)}")

    async def upload_multiple_photos(
        self, 
        files: list[UploadFile], 
        folder: str, 
        user_id: str,
        max_width: int = 1200,
        max_height: int = 800
    ) -> list[Dict[str, str]]:
        """Subir múltiples fotos"""
        if len(files) > 10:
            raise InvalidFileTypeException("Máximo 10 fotos por vez")
        
        results = []
        for file in files:
            self._validate_image_file(file)
            
            try:
                file_content = await file.read()
                
                result = cloudinary.uploader.upload(
                    file_content,
                    folder=f"voyaj/{folder}",
                    transformation=[
                        {"width": max_width, "height": max_height, "crop": "limit"},
                        {"quality": "auto", "fetch_format": "auto"}
                    ],
                    context=f"user_id={user_id}"
                )
                
                results.append({
                    "url": result["secure_url"],
                    "public_id": result["public_id"],
                    "original_name": file.filename
                })
                
            except Exception as e:
                raise CloudinaryException(f"Error subiendo {file.filename}: {str(e)}")
        
        return results

    async def delete_file(self, public_id: str, resource_type: str = "image") -> bool:
        """Eliminar archivo de Cloudinary"""
        try:
            result = cloudinary.uploader.destroy(public_id, resource_type=resource_type)
            return result.get("result") == "ok"
        except Exception:
            return False

    def _validate_image_file(self, file: UploadFile) -> None:
        """Validar archivo de imagen"""
        if file.content_type not in self.allowed_image_types:
            raise InvalidFileTypeException(
                f"Tipo de archivo no válido. Permitidos: {', '.join(self.allowed_image_types)}"
            )
        
        if file.size and file.size > self.max_file_size:
            raise FileTooLargeException(
                f"Archivo demasiado grande. Máximo: {self.max_file_size / (1024*1024):.1f}MB"
            )

    def _validate_document_file(self, file: UploadFile) -> None:
        """Validar archivo de documento"""
        if file.content_type not in self.allowed_document_types:
            raise InvalidFileTypeException(
                f"Tipo de archivo no válido. Permitidos: {', '.join(self.allowed_document_types)}"
            )
        
        if file.size and file.size > self.max_file_size * 2:  # 10MB para documentos
            raise FileTooLargeException(
                f"Documento demasiado grande. Máximo: {(self.max_file_size * 2) / (1024*1024):.1f}MB"
            )