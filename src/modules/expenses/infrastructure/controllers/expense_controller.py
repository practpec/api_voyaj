from fastapi import HTTPException
from typing import Optional
from ...application.dtos.expense_dto import (
    CreateExpenseDTO, UpdateExpenseDTO, ChangeExpenseStatusDTO,
    ExpenseResponseDTO, TripExpensesResponseDTO, ExpenseSummaryDTO
)
from ...application.use_cases.create_expense import CreateExpenseUseCase
from ...application.use_cases.get_expense import GetExpenseUseCase
from ...application.use_cases.get_trip_expenses import GetTripExpensesUseCase
from ...application.use_cases.update_expense import UpdateExpenseUseCase
from ...application.use_cases.change_expense_status import ChangeExpenseStatusUseCase
from ...application.use_cases.delete_expense import DeleteExpenseUseCase
from ...application.use_cases.get_expense_summary import GetExpenseSummaryUseCase
from shared.errors.custom_errors import ValidationError, NotFoundError, ForbiddenError


class ExpenseController:
    def __init__(
        self,
        create_expense_use_case: CreateExpenseUseCase,
        get_expense_use_case: GetExpenseUseCase,
        get_trip_expenses_use_case: GetTripExpensesUseCase,
        update_expense_use_case: UpdateExpenseUseCase,
        change_expense_status_use_case: ChangeExpenseStatusUseCase,
        delete_expense_use_case: DeleteExpenseUseCase,
        get_expense_summary_use_case: GetExpenseSummaryUseCase
    ):
        self._create_expense_use_case = create_expense_use_case
        self._get_expense_use_case = get_expense_use_case
        self._get_trip_expenses_use_case = get_trip_expenses_use_case
        self._update_expense_use_case = update_expense_use_case
        self._change_expense_status_use_case = change_expense_status_use_case
        self._delete_expense_use_case = delete_expense_use_case
        self._get_expense_summary_use_case = get_expense_summary_use_case

    async def create_expense(self, dto: CreateExpenseDTO, current_user: dict) -> ExpenseResponseDTO:
        """Crear nuevo gasto"""
        try:
            return await self._create_expense_use_case.execute(dto=dto, user_id=current_user["id"])
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ForbiddenError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    async def get_expense(self, expense_id: str, current_user: dict) -> ExpenseResponseDTO:
        """Obtener gasto por ID"""
        try:
            return await self._get_expense_use_case.execute(expense_id=expense_id, user_id=current_user["id"])
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ForbiddenError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    async def get_trip_expenses(self, trip_id: str, category: Optional[str], current_user: dict) -> TripExpensesResponseDTO:
        """Obtener gastos de un viaje"""
        try:
            return await self._get_trip_expenses_use_case.execute(trip_id=trip_id, user_id=current_user["id"], category=category)
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ForbiddenError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    async def update_expense(self, expense_id: str, dto: UpdateExpenseDTO, current_user: dict) -> ExpenseResponseDTO:
        """Actualizar gasto"""
        try:
            return await self._update_expense_use_case.execute(expense_id=expense_id, dto=dto, user_id=current_user["id"])
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ForbiddenError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    async def change_expense_status(self, expense_id: str, dto: ChangeExpenseStatusDTO, current_user: dict) -> ExpenseResponseDTO:
        """Cambiar estado del gasto"""
        try:
            return await self._change_expense_status_use_case.execute(expense_id=expense_id, dto=dto, user_id=current_user["id"])
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ForbiddenError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    async def delete_expense(self, expense_id: str, current_user: dict) -> dict:
        """Eliminar gasto"""
        try:
            await self._delete_expense_use_case.execute(expense_id=expense_id, user_id=current_user["id"])
            return {"message": "Gasto eliminado exitosamente"}
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ForbiddenError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    async def get_expense_summary(self, trip_id: str, current_user: dict) -> ExpenseSummaryDTO:
        """Obtener resumen de gastos del viaje"""
        try:
            return await self._get_expense_summary_use_case.execute(trip_id=trip_id, user_id=current_user["id"])
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ForbiddenError as e:
            raise HTTPException(status_code=403, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

    async def health_check(self) -> dict:
        """Health check del módulo de gastos"""
        return {
            "module": "expenses",
            "status": "healthy",
            "version": "1.0.0",
            "features": ["create_expense", "get_expense", "update_expense", "delete_expense", "trip_expenses", "expense_summary", "change_status"]
        }