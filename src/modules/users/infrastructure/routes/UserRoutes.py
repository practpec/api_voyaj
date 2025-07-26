from fastapi import APIRouter, Depends, UploadFile, File, Query
from ..controllers.UserController import UserController
from ...application.dtos.UserDTOs import (
    CreateUserDTO, 
    LoginDTO, 
    UpdateProfileDTO,
    VerifyEmailDTO,
    ResendVerificationDTO,
    RequestPasswordResetDTO,
    ResetPasswordDTO
)
from shared.middleware.AuthMiddleware import get_current_user
from shared.repositories.RepositoryFactory import RepositoryFactory
from shared.services.ServiceFactory import ServiceFactory
from shared.controllers.UploadController import UploadController

router = APIRouter()

def get_user_controller():
    return UserController(
        user_repository=RepositoryFactory.get_user_repository(),
        auth_service=ServiceFactory.get_auth_service(),
        email_service=ServiceFactory.get_email_service()
    )

def get_upload_controller():
    return UploadController()

# Endpoints públicos
@router.post("/register")
async def register(
    user_data: CreateUserDTO,
    controller: UserController = Depends(get_user_controller)
):
    return await controller.register(user_data)

@router.post("/login")
async def login(
    login_data: LoginDTO,
    controller: UserController = Depends(get_user_controller)
):
    return await controller.login(login_data)

@router.post("/verify-email")
async def verify_email(
    verify_data: VerifyEmailDTO,
    controller: UserController = Depends(get_user_controller)
):
    return await controller.verify_email(verify_data)

@router.post("/resend-verification")
async def resend_verification(
    resend_data: ResendVerificationDTO,
    controller: UserController = Depends(get_user_controller)
):
    return await controller.resend_verification(resend_data)

@router.post("/forgot-password")
async def request_password_reset(
    reset_request: RequestPasswordResetDTO,
    controller: UserController = Depends(get_user_controller)
):
    return await controller.request_password_reset(reset_request)

@router.post("/reset-password")
async def reset_password(
    reset_data: ResetPasswordDTO,
    controller: UserController = Depends(get_user_controller)
):
    return await controller.reset_password(reset_data)

# Endpoints protegidos
@router.get("/profile")
async def get_profile(
    controller: UserController = Depends(get_user_controller),
    current_user: dict = Depends(get_current_user)
):
    return await controller.get_profile(current_user)

@router.put("/profile")
async def update_profile(
    profile_data: UpdateProfileDTO,
    controller: UserController = Depends(get_user_controller),
    current_user: dict = Depends(get_current_user)
):
    return await controller.update_profile(profile_data, current_user)

@router.post("/profile/picture")
async def upload_profile_picture(
    file: UploadFile = File(...),
    upload_controller: UploadController = Depends(get_upload_controller),
    current_user: dict = Depends(get_current_user)
):
    return await upload_controller.upload_profile_picture(file, current_user)

@router.get("/search")
async def search_users(
    query: str = Query(..., min_length=2),
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
    controller: UserController = Depends(get_user_controller)
):
    return await controller.search_users(query, limit, offset)