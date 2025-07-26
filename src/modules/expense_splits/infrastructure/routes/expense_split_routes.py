# src/modules/expense_splits/infrastructure/routes/expense_split_routes.py
from fastapi import APIRouter, Depends, Path
from ..controllers.expense_split_controller import ExpenseSplitController
from ...application.dtos.expense_split_dto import UpdateExpenseSplitsDTO, MarkSplitAsPaidDTO, ChangeExpenseSplitStatusDTO
from shared.middleware.AuthMiddleware import get_current_user
from shared.repositories.RepositoryFactory import RepositoryFactory
from shared.services.ServiceFactory import ServiceFactory
from ...application.use_cases.get_expense_splits import GetExpenseSplitsUseCase
from ...application.use_cases.update_expense_splits import UpdateExpenseSplitsUseCase
from ...application.use_cases.mark_split_as_paid import MarkSplitAsPendingUseCase
from ...application.use_cases.change_split_status import ChangeSplitStatusUseCase
from ...application.use_cases.get_trip_balances import GetTripBalancesUseCase

router = APIRouter()

def get_expense_split_controller():
    expense_split_repo = RepositoryFactory.get_expense_split_repository()
    expense_split_service = ServiceFactory.get_expense_split_service()
    
    get_expense_splits_use_case = GetExpenseSplitsUseCase(
        expense_split_repository=expense_split_repo
    )
    
    update_expense_splits_use_case = UpdateExpenseSplitsUseCase(
        expense_split_repository=expense_split_repo,
        expense_split_service=expense_split_service
    )
    
    mark_split_as_paid_use_case = MarkSplitAsPendingUseCase(
        expense_split_repository=expense_split_repo,
        expense_split_service=expense_split_service
    )
    
    change_split_status_use_case = ChangeSplitStatusUseCase(
        expense_split_repository=expense_split_repo,
        expense_split_service=expense_split_service
    )
    
    get_trip_balances_use_case = GetTripBalancesUseCase(
        expense_split_repository=expense_split_repo,
        expense_split_service=expense_split_service
    )
    
    return ExpenseSplitController(
        get_expense_splits_use_case=get_expense_splits_use_case,
        update_expense_splits_use_case=update_expense_splits_use_case,
        mark_split_as_paid_use_case=mark_split_as_paid_use_case,
        change_split_status_use_case=change_split_status_use_case,
        get_trip_balances_use_case=get_trip_balances_use_case
    )

@router.get("/expenses/{expense_id}/splits")
async def get_expense_splits(
    expense_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
    controller: ExpenseSplitController = Depends(get_expense_split_controller)
):
    return await controller.get_expense_splits(expense_id, current_user)

@router.put("/expenses/{expense_id}/splits")
async def update_expense_splits(
    expense_id: str = Path(...),
    dto: UpdateExpenseSplitsDTO = None,
    current_user: dict = Depends(get_current_user),
    controller: ExpenseSplitController = Depends(get_expense_split_controller)
):
    return await controller.update_expense_splits(expense_id, dto, current_user)

@router.post("/splits/{expense_split_id}/settle")
async def mark_split_as_paid(
    expense_split_id: str = Path(...),
    dto: MarkSplitAsPaidDTO = None,
    current_user: dict = Depends(get_current_user),
    controller: ExpenseSplitController = Depends(get_expense_split_controller)
):
    return await controller.mark_split_as_paid(expense_split_id, dto, current_user)

@router.put("/splits/{expense_split_id}/status")
async def change_split_status(
    expense_split_id: str = Path(...),
    dto: ChangeExpenseSplitStatusDTO = None,
    current_user: dict = Depends(get_current_user),
    controller: ExpenseSplitController = Depends(get_expense_split_controller)
):
    return await controller.change_split_status(expense_split_id, dto, current_user)

@router.get("/trips/{trip_id}/balances")
async def get_trip_balances(
    trip_id: str = Path(...),
    current_user: dict = Depends(get_current_user),
    controller: ExpenseSplitController = Depends(get_expense_split_controller)
):
    return await controller.get_trip_balances(trip_id, current_user)

@router.get("/health")
async def health_check(
    controller: ExpenseSplitController = Depends(get_expense_split_controller)
):
    return await controller.health_check()