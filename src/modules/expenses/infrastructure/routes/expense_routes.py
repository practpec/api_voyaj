from fastapi import APIRouter, Depends, Query, Path, Body
from typing import Dict, Any, Optional
from ..controllers.expense_controller import ExpenseController
from ...application.dtos.create_expense_dto import CreateExpenseDTO
from ...application.dtos.update_expense_dto import UpdateExpenseDTO
from shared.middleware.AuthMiddleware import get_current_user
from shared.repositories.RepositoryFactory import RepositoryFactory
from shared.services.ServiceFactory import ServiceFactory
from shared.events.event_bus import EventBus

from ...application.use_cases.create_expense import CreateExpense
from ...application.use_cases.update_expense import UpdateExpense
from ...application.use_cases.delete_expense import DeleteExpense
from ...application.use_cases.get_expense import GetExpense
from ...application.use_cases.get_trip_expenses import GetTripExpenses

router = APIRouter()

def get_expense_controller():
    expense_repo = RepositoryFactory.get_expense_repository()
    expense_service = ServiceFactory.get_expense_service()
    event_bus = EventBus.get_instance()
    
    create_expense_use_case = CreateExpense(expense_repo, expense_service, event_bus)
    update_expense_use_case = UpdateExpense(expense_repo, expense_service, event_bus)
    delete_expense_use_case = DeleteExpense(expense_repo, expense_service, event_bus)
    get_expense_use_case = GetExpense(expense_repo)
    get_trip_expenses_use_case = GetTripExpenses(expense_repo, expense_service)
    
    return ExpenseController(
        create_expense_use_case,
        update_expense_use_case,
        delete_expense_use_case,
        get_expense_use_case,
        get_trip_expenses_use_case
    )

@router.post("", summary="Crear gasto")
async def create_expense(
    request: Dict[str, Any] = Body(...),
    controller: ExpenseController = Depends(get_expense_controller),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    return await controller.create_expense(request, current_user)

@router.get("/{expense_id}", summary="Obtener gasto")
async def get_expense(
    expense_id: str = Path(...),
    controller: ExpenseController = Depends(get_expense_controller),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    return await controller.get_expense(expense_id, current_user)

@router.put("/{expense_id}", summary="Actualizar gasto")
async def update_expense(
    expense_id: str = Path(...),
    request: Dict[str, Any] = Body(...),
    controller: ExpenseController = Depends(get_expense_controller),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    return await controller.update_expense(expense_id, request, current_user)

@router.delete("/{expense_id}", summary="Eliminar gasto")
async def delete_expense(
    expense_id: str = Path(...),
    controller: ExpenseController = Depends(get_expense_controller),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    return await controller.delete_expense(expense_id, current_user)

@router.get("/trips/{trip_id}", summary="Gastos del viaje")
async def get_trip_expenses(
    trip_id: str = Path(...),
    category: Optional[str] = Query(None),
    user_filter: Optional[str] = Query(None),
    include_summary: bool = Query(True),
    controller: ExpenseController = Depends(get_expense_controller),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    return await controller.get_trip_expenses(
        trip_id, current_user, category, user_filter, include_summary
    )

@router.get("/categories/available", summary="Categorías disponibles")
async def get_available_categories(
    controller: ExpenseController = Depends(get_expense_controller)
):
    return await controller.get_available_categories()

@router.post("/{expense_id}/confirm", summary="Confirmar gasto")
async def confirm_expense(
    expense_id: str = Path(...),
    controller: ExpenseController = Depends(get_expense_controller),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    return {"message": "Funcionalidad disponible próximamente"}

@router.post("/{expense_id}/receipt", summary="Subir comprobante")
async def upload_receipt(
    expense_id: str = Path(...),
    receipt_data: Dict[str, Any] = Body(...),
    controller: ExpenseController = Depends(get_expense_controller),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    return {"message": "Funcionalidad disponible próximamente"}

@router.get("/trips/{trip_id}/summary", summary="Resumen financiero")
async def get_financial_summary(
    trip_id: str = Path(...),
    controller: ExpenseController = Depends(get_expense_controller),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    return {"message": "Funcionalidad disponible próximamente"}

@router.get("/trips/{trip_id}/timeline", summary="Timeline de gastos")
async def get_expenses_timeline(
    trip_id: str = Path(...),
    controller: ExpenseController = Depends(get_expense_controller),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    return {"message": "Funcionalidad disponible próximamente"}