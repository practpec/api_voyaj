from fastapi import APIRouter, Depends, Query, Path
from typing import Optional
from ..controllers.expense_controller import ExpenseController
from ...application.dtos.expense_dto import CreateExpenseDTO, UpdateExpenseDTO, ChangeExpenseStatusDTO
from shared.middleware.AuthMiddleware import get_current_user
from shared.repositories.RepositoryFactory import RepositoryFactory

from ...application.use_cases.create_expense import CreateExpenseUseCase
from ...application.use_cases.get_expense import GetExpenseUseCase
from ...application.use_cases.get_trip_expenses import GetTripExpensesUseCase
from ...application.use_cases.update_expense import UpdateExpenseUseCase
from ...application.use_cases.change_expense_status import ChangeExpenseStatusUseCase
from ...application.use_cases.delete_expense import DeleteExpenseUseCase
from ...application.use_cases.get_expense_summary import GetExpenseSummaryUseCase
from ...domain.expense_service import ExpenseService

router = APIRouter()

def get_expense_controller():
    expense_repo = RepositoryFactory.get_expense_repository()
    trip_member_repo = RepositoryFactory.get_trip_member_repository()
    user_repo = RepositoryFactory.get_user_repository()
    trip_repo = RepositoryFactory.get_trip_repository()
    
    expense_service = ExpenseService(
        expense_repository=expense_repo,
        trip_member_repository=trip_member_repo,
        user_repository=user_repo,
        trip_repository=trip_repo
    )
    
    create_expense_use_case = CreateExpenseUseCase(
        expense_repository=expense_repo,
        expense_service=expense_service
    )
    
    get_expense_use_case = GetExpenseUseCase(
        expense_repository=expense_repo,
        expense_service=expense_service,
        user_repository=user_repo
    )
    
    get_trip_expenses_use_case = GetTripExpensesUseCase(
        expense_repository=expense_repo,
        expense_service=expense_service,
        trip_member_repository=trip_member_repo
    )
    
    update_expense_use_case = UpdateExpenseUseCase(
        expense_repository=expense_repo,
        expense_service=expense_service
    )
    
    change_expense_status_use_case = ChangeExpenseStatusUseCase(
        expense_repository=expense_repo,
        expense_service=expense_service
    )
    
    delete_expense_use_case = DeleteExpenseUseCase(
        expense_repository=expense_repo,
        expense_service=expense_service
    )
    
    get_expense_summary_use_case = GetExpenseSummaryUseCase(
        expense_repository=expense_repo,
        expense_service=expense_service,
        trip_member_repository=trip_member_repo
    )
    
    return ExpenseController(
        create_expense_use_case=create_expense_use_case,
        get_expense_use_case=get_expense_use_case,
        get_trip_expenses_use_case=get_trip_expenses_use_case,
        update_expense_use_case=update_expense_use_case,
        change_expense_status_use_case=change_expense_status_use_case,
        delete_expense_use_case=delete_expense_use_case,
        get_expense_summary_use_case=get_expense_summary_use_case
    )

@router.post("/")
async def create_expense(
    dto: CreateExpenseDTO,
    current_user: dict = Depends(get_current_user),
    controller: ExpenseController = Depends(get_expense_controller)
):
    return await controller.create_expense(dto, current_user)

@router.get("/{expense_id}")
async def get_expense(
    expense_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
    controller: ExpenseController = Depends(get_expense_controller)
):
    return await controller.get_expense(expense_id, current_user)

@router.put("/{expense_id}")
async def update_expense(
    expense_id: str = Path(...),
    dto: UpdateExpenseDTO = None,
    current_user: dict = Depends(get_current_user),
    controller: ExpenseController = Depends(get_expense_controller)
):
    return await controller.update_expense(expense_id, dto, current_user)

@router.delete("/{expense_id}")
async def delete_expense(
    expense_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
    controller: ExpenseController = Depends(get_expense_controller)
):
    return await controller.delete_expense(expense_id, current_user)

@router.put("/{expense_id}/status")
async def change_expense_status(
    expense_id: str = Path(...),
    dto: ChangeExpenseStatusDTO = None,
    current_user: dict = Depends(get_current_user),
    controller: ExpenseController = Depends(get_expense_controller)
):
    return await controller.change_expense_status(expense_id, dto, current_user)

@router.get("/trip/{trip_id}")
async def get_trip_expenses(
    trip_id: str = Path(...),
    category: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    controller: ExpenseController = Depends(get_expense_controller)
):
    return await controller.get_trip_expenses(trip_id, category, current_user)

@router.get("/trip/{trip_id}/summary")
async def get_expense_summary(
    trip_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
    controller: ExpenseController = Depends(get_expense_controller)
):
    return await controller.get_expense_summary(trip_id, current_user)

@router.get("/health")
async def health_check(
    controller: ExpenseController = Depends(get_expense_controller)
):
    return await controller.health_check()