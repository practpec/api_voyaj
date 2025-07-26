from fastapi import APIRouter, Depends, Query, Path
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
    user_repo = RepositoryFactory.get_user_repository()
    trip_repo = RepositoryFactory.get_trip_repository()
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
    request: Dict[str, Any],
    controller: ExpenseController = Depends(get_expense_controller),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Crear un nuevo gasto.
    
    **Campos requeridos:**
    - **trip_id**: ID del viaje
    - **amount**: Monto (decimal)
    - **currency**: Código de moneda (ISO 3 letras)
    - **category**: Categoría del gasto
    - **description**: Descripción del gasto
    - **expense_date**: Fecha del gasto (ISO format)
    
    **Campos opcionales:**
    - **is_shared**: Si es gasto compartido (default: false)
    - **paid_by_user_id**: Quien pagó (default: usuario actual)
    - **activity_id**: ID de actividad asociada
    - **diary_entry_id**: ID de entrada de diario asociada
    - **location**: Ubicación del gasto
    - **receipt_url**: URL del comprobante
    - **metadata**: Datos adicionales
    """
    return await controller.create_expense(request, current_user)

@router.get("/{expense_id}", summary="Obtener gasto")
async def get_expense(
    expense_id: str = Path(...),
    controller: ExpenseController = Depends(get_expense_controller),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Obtener detalles de un gasto específico.
    
    - **expense_id**: ID del gasto a consultar
    
    Retorna información completa del gasto incluyendo:
    - Datos básicos (monto, categoría, descripción)
    - Asociaciones (actividad, diario)
    - Permisos (si puede editar, dividir)
    - Metadatos y comprobantes
    """
    return await controller.get_expense(expense_id, current_user)

@router.put("/{expense_id}", summary="Actualizar gasto")
async def update_expense(
    expense_id: str = Path(...),
    request: Dict[str, Any],
    controller: ExpenseController = Depends(get_expense_controller),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Actualizar un gasto existente.
    
    - **expense_id**: ID del gasto a actualizar
    
    **Campos actualizables:**
    - **amount**: Nuevo monto
    - **currency**: Nueva moneda
    - **category**: Nueva categoría
    - **description**: Nueva descripción
    - **location**: Nueva ubicación
    - **is_shared**: Cambiar si es compartido
    - **paid_by_user_id**: Cambiar quien pagó
    - **activity_id**: Asociar/desasociar actividad
    - **diary_entry_id**: Asociar/desasociar entrada diario
    - **metadata**: Actualizar metadatos
    
    Solo los campos proporcionados serán actualizados.
    """
    return await controller.update_expense(expense_id, request, current_user)

@router.delete("/{expense_id}", summary="Eliminar gasto")
async def delete_expense(
    expense_id: str = Path(...),
    controller: ExpenseController = Depends(get_expense_controller),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Eliminar un gasto (eliminación suave).
    
    - **expense_id**: ID del gasto a eliminar
    
    El gasto no se elimina físicamente, sino que se marca como eliminado.
    Solo el usuario que creó el gasto o quien lo pagó puede eliminarlo.
    """
    return await controller.delete_expense(expense_id, current_user)

@router.get("/trips/{trip_id}", summary="Gastos del viaje")
async def get_trip_expenses(
    trip_id: str = Path(...),
    controller: ExpenseController = Depends(get_expense_controller),
    current_user: Dict[str, Any] = Depends(get_current_user),
    category: Optional[str] = Query(None, description="Filtrar por categoría"),
    user_filter: Optional[str] = Query(None, description="Filtrar por usuario"),
    include_summary: bool = Query(True, description="Incluir resumen financiero")
):
    """
    Obtener todos los gastos de un viaje con filtros opcionales.
    
    - **trip_id**: ID del viaje
    
    **Parámetros de consulta:**
    - **category**: Filtrar por categoría específica
    - **user_filter**: Filtrar por usuario específico
    - **include_summary**: Incluir resumen con totales y estadísticas
    
    **Respuesta incluye:**
    - Lista de gastos con información detallada
    - Resumen financiero (si se solicita):
      - Total por moneda
      - Gastos por categoría
      - Cantidad de gastos compartidos
      - Gastos con/sin comprobante
    """
    return await controller.get_trip_expenses(
        trip_id, current_user, category, user_filter, include_summary
    )

@router.get("/categories/available", summary="Categorías disponibles")
async def get_available_categories(
    controller: ExpenseController = Depends(get_expense_controller)
):
    """
    Obtener lista de categorías disponibles para gastos.
    
    Retorna todas las categorías válidas con sus valores
    internos y nombres para mostrar en la interfaz.
    
    **Categorías disponibles:**
    - Transporte
    - Alojamiento
    - Comida
    - Actividades
    - Compras
    - Salud
    - Comunicación
    - Seguros
    - Emergencia
    - Otros
    """
    return await controller.get_available_categories()

# Rutas adicionales para funcionalidades específicas

@router.post("/{expense_id}/confirm", summary="Confirmar gasto")
async def confirm_expense(
    expense_id: str = Path(...),
    controller: ExpenseController = Depends(get_expense_controller),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Confirmar un gasto pendiente.
    
    Cambia el estado del gasto de "pending" a "confirmed".
    Solo gastos confirmados pueden ser divididos entre usuarios.
    """
    # Esta funcionalidad se puede implementar más adelante
    return {"message": "Funcionalidad disponible próximamente"}

@router.post("/{expense_id}/receipt", summary="Subir comprobante")
async def upload_receipt(
    expense_id: str = Path(...),
    receipt_data: Dict[str, Any],
    controller: ExpenseController = Depends(get_expense_controller),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Subir comprobante para un gasto.
    
    **Campos requeridos:**
    - **receipt_url**: URL del comprobante subido
    
    Se recomienda usar el endpoint de upload general primero
    para subir el archivo y luego usar esta ruta para asociarlo.
    """
    # Esta funcionalidad se puede implementar más adelante
    return {"message": "Funcionalidad disponible próximamente"}

@router.get("/trips/{trip_id}/summary", summary="Resumen financiero")
async def get_financial_summary(
    trip_id: str = Path(...),
    controller: ExpenseController = Depends(get_expense_controller),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Obtener resumen financiero detallado del viaje.
    
    **Incluye:**
    - Total de gastos por moneda
    - Gastos por categoría
    - Promedio de gasto diario
    - Gastos más altos
    - Timeline de gastos
    - Estadísticas de gastos compartidos
    """
    # Esta funcionalidad se puede implementar más adelante
    return {"message": "Funcionalidad disponible próximamente"}

@router.get("/trips/{trip_id}/timeline", summary="Timeline de gastos")
async def get_expenses_timeline(
    trip_id: str = Path(...),
    controller: ExpenseController = Depends(get_expense_controller),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Obtener timeline cronológico de gastos del viaje.
    
    Retorna los gastos ordenados por fecha con información
    relevante para crear una línea temporal visual.
    """
    # Esta funcionalidad se puede implementar más adelante
    return {"message": "Funcionalidad disponible próximamente"}