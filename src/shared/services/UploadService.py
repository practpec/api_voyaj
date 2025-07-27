# src/shared/services/UploadService.py
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
        """Subir imagen de perfil a Cloudinary"""
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
            raise CloudinaryException(f"Error al subir imagen: {str(e)}")

    async def delete_file(self, public_id: str, resource_type: str = "image") -> bool:
        """Eliminar archivo de Cloudinary"""
        try:
            result = cloudinary.uploader.destroy(public_id, resource_type=resource_type)
            return result.get("result") == "ok"
        except Exception as e:
            raise CloudinaryException(f"Error al eliminar archivo: {str(e)}")

    def extract_public_id_from_url(self, url: str) -> Optional[str]:
        """Extraer public_id de una URL de Cloudinary"""
        try:
            # URL ejemplo: https://res.cloudinary.com/cloud_name/image/upload/v123456789/voyaj/profiles/user_id/profile_user_id.webp
            parts = url.split('/')
            if 'voyaj' in parts:
                voyaj_index = parts.index('voyaj')
                public_id_parts = parts[voyaj_index:]
                public_id = '/'.join(public_id_parts)
                # Remover extensión
                if '.' in public_id:
                    public_id = public_id.rsplit('.', 1)[0]
                return public_id
        except Exception:
            pass
        return None

    async def upload_trip_photos(self, trip_id: str, files: list[UploadFile], user_id: str) -> Dict[str, Any]:
        """Subir múltiples fotos de viaje"""
        if len(files) > 10:
            raise InvalidFileTypeException("Máximo 10 archivos por subida")

        uploaded_photos = []
        failed_uploads = []

        for file in files:
            try:
                self._validate_image_file(file)
                
                file_content = await file.read()
                
                result = cloudinary.uploader.upload(
                    file_content,
                    folder=f"voyaj/trips/{trip_id}/photos",
                    transformation=[
                        {"width": 1200, "height": 800, "crop": "limit"},
                        {"quality": "auto", "fetch_format": "auto"}
                    ],
                    use_filename=True,
                    unique_filename=True
                )
                
                uploaded_photos.append({
                    "filename": file.filename,
                    "url": result["secure_url"],
                    "public_id": result["public_id"]
                })
                
            except Exception as e:
                failed_uploads.append({
                    "filename": file.filename,
                    "error": str(e)
                })

        if not uploaded_photos and failed_uploads:
            raise UploadFailedException("No se pudo subir ninguna foto")

        return {
            "uploaded": uploaded_photos,
            "failed": failed_uploads,
            "total_uploaded": len(uploaded_photos),
            "total_failed": len(failed_uploads)
        }

    async def upload_document(self, folder: str, file: UploadFile, user_id: str) -> Dict[str, str]:
        """Subir documento a carpeta específica"""
        self._validate_document_file(file)
        
        try:
            file_content = await file.read()
            
            result = cloudinary.uploader.upload(
                file_content,
                folder=f"voyaj/documents/{user_id}/{folder}",
                resource_type="raw",
                use_filename=True,
                unique_filename=True
            )
            
            return {
                "url": result["secure_url"],
                "public_id": result["public_id"],
                "filename": file.filename
            }
            
        except Exception as e:
            raise CloudinaryException(f"Error al subir documento: {str(e)}")

    def _validate_image_file(self, file: UploadFile) -> None:
        """Validar archivo de imagen"""
        if file.content_type not in self.allowed_image_types:
            raise InvalidFileTypeException(
                f"Tipo de archivo no permitido. Tipos permitidos: {', '.join(self.allowed_image_types)}"
            )
        
        if file.size and file.size > self.max_file_size:
            raise FileTooLargeException(
                f"Archivo muy grande. Tamaño máximo: {self.max_file_size // (1024*1024)}MB"
            )

    def _validate_document_file(self, file: UploadFile) -> None:
        """Validar archivo de documento"""
        if file.content_type not in self.allowed_document_types:
            raise InvalidFileTypeException(
                f"Tipo de archivo no permitido. Tipos permitidos: {', '.join(self.allowed_document_types)}"
            )
        
        max_doc_size = 10 * 1024 * 1024  # 10MB para documentos
        if file.size and file.size > max_doc_size:
            raise FileTooLargeException(
                f"Archivo muy grande. Tamaño máximo: {max_doc_size // (1024*1024)}MB"
            )