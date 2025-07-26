from fastapi import HTTPException, status
from typing import Dict, Any, Optional
from datetime import datetime
from decimal import Decimal
from ..application.use_cases.create_expense import CreateExpense
from ..application.use_cases.update_expense import UpdateExpense
from ..application.use_cases.delete_expense import DeleteExpense
from ..application.use_cases.get_expense import GetExpense
from ..application.use_cases.get_trip_expenses import GetTripExpenses
from ..application.dtos.create_expense_dto import CreateExpenseDTO
from ..application.dtos.update_expense_dto import UpdateExpenseDTO
from shared.errors.custom_errors import ValidationError, NotFoundError, AuthorizationError


class ExpenseController:
    def __init__(
        self,
        create_expense_use_case: CreateExpense,
        update_expense_use_case: UpdateExpense,
        delete_expense_use_case: DeleteExpense,
        get_expense_use_case: GetExpense,
        get_trip_expenses_use_case: GetTripExpenses
    ):
        self._create_expense = create_expense_use_case
        self._update_expense = update_expense_use_case
        self._delete_expense = delete_expense_use_case
        self._get_expense = get_expense_use_case
        self._get_trip_expenses = get_trip_expenses_use_case

    async def create_expense(self, request_data: Dict[str, Any], current_user: Dict[str, Any]) -> Dict[str, Any]:
        """Crear nuevo gasto"""
        try:
            # Convertir fecha si viene como string
            if isinstance(request_data.get("expense_date"), str):
                request_data["expense_date"] = datetime.fromisoformat(request_data["expense_date"].replace("Z", "+00:00"))

            dto = CreateExpenseDTO.from_dict(request_data)
            result = await self._create_expense.execute(dto, current_user["id"])
            return result

        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "Datos inválidos", "message": str(e)}
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"error": "Error interno", "message": str(e)}
            )

    async def update_expense(
        self, 
        expense_id: str, 
        request_data: Dict[str, Any], 
        current_user: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Actualizar gasto existente"""
        try:
            dto = UpdateExpenseDTO.from_dict(request_data)
            
            if not dto.has_updates():
                raise ValidationError("No se proporcionaron campos para actualizar")

            result = await self._update_expense.execute(expense_id, dto, current_user["id"])
            return result

        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "Datos inválidos", "message": str(e)}
            )
        except NotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "No encontrado", "message": str(e)}
            )
        except AuthorizationError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"error": "No autorizado", "message": str(e)}
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"error": "Error interno", "message": str(e)}
            )

    async def delete_expense(self, expense_id: str, current_user: Dict[str, Any]) -> Dict[str, Any]:
        """Eliminar gasto"""
        try:
            result = await self._delete_expense.execute(expense_id, current_user["id"])
            return result

        except NotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "No encontrado", "message": str(e)}
            )
        except AuthorizationError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"error": "No autorizado", "message": str(e)}
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"error": "Error interno", "message": str(e)}
            )

    async def get_expense(self, expense_id: str, current_user: Dict[str, Any]) -> Dict[str, Any]:
        """Obtener detalles de gasto"""
        try:
            result = await self._get_expense.execute(expense_id, current_user["id"])
            return result

        except NotFoundError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "No encontrado", "message": str(e)}
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"error": "Error interno", "message": str(e)}
            )

    async def get_trip_expenses(
        self, 
        trip_id: str, 
        current_user: Dict[str, Any],
        category: Optional[str] = None,
        user_filter: Optional[str] = None,
        include_summary: bool = True
    ) -> Dict[str, Any]:
        """Obtener gastos de un viaje"""
        try:
            result = await self._get_trip_expenses.execute(
                trip_id=trip_id,
                user_id=current_user["id"],
                include_summary=include_summary,
                category_filter=category,
                user_filter=user_filter
            )
            return result

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"error": "Error interno", "message": str(e)}
            )

    async def get_available_categories(self) -> Dict[str, Any]:
        """Obtener categorías disponibles para gastos"""
        try:
            from ..domain.expense import ExpenseCategory
            
            categories = []
            for category in ExpenseCategory:
                categories.append({
                    "value": category.value,
                    "display": self._get_category_display_name(category)
                })

            return {
                "success": True,
                "data": {
                    "categories": categories
                }
            }

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"error": "Error interno", "message": str(e)}
            )

    def _get_category_display_name(self, category) -> str:
        """Obtener nombre de categoría para mostrar"""
        names = {
            "transportation": "Transporte",
            "accommodation": "Alojamiento",
            "food": "Comida",
            "activities": "Actividades",
            "shopping": "Compras",
            "healthcare": "Salud",
            "communication": "Comunicación",
            "insurance": "Seguros",
            "emergency": "Emergencia",
            "other": "Otros"
        }
        return names.get(category.value, "Otros")