Crear el entorno virtual:

python -m venv venv

Activar el entorno virtual:

.\venv\Scripts\activate


Instalar dependencias:

pip install -r requirements.txt


uvicorn src.main:app --reload


Analizando el estado actual del repositorio contra el plan de creación:

## ENTIDADES IMPLEMENTADAS ✅

### 1. USERS (Completa)
- ✅ Domain: User.py con entidad completa
- ✅ Application: DTOs y casos de uso (CreateUser, LoginUser, UpdateProfile, etc.)
- ✅ Infrastructure: UserController.py, UserMongoRepository.py, rutas

### 2. FRIENDSHIPS (Completa) 
- ✅ Domain: friendship.py, friendship_service.py, eventos
- ✅ Application: DTOs y casos de uso completos
- ✅ Infrastructure: controladores, repositorio Mongo, rutas

### 3. TRIPS (Completa)
- ✅ Domain: trip.py, trip_member.py, trip_service.py, eventos
- ✅ Application: DTOs y casos de uso completos  
- ✅ Infrastructure: controladores, repositorios Mongo, rutas

## SHARED IMPLEMENTADO ✅
- ✅ Database/Connection.py
- ✅ Services (Auth, Email, Upload)
- ✅ Events/event_bus.py
- ✅ Exceptions personalizadas
- ✅ Utils (validation, pagination, response)
- ✅ Middleware (Auth, Error)
- ✅ Templates de email

## ENTIDADES FALTANTES (según plan de 15 fases)

### FASE 6: DAYS 📅
- **Tabla BD**: `dias`
- **Dependencias**: `viajes` ✅

### FASE 7: ACTIVITIES 🎯  
- **Tabla BD**: `actividades`
- **Dependencias**: `dias` → `viajes`

### FASE 8: DIARY_ENTRIES 📖
- **Tabla BD**: `entradas_diario` 
- **Dependencias**: `dias` + `usuarios` ✅

### FASE 9: EXPENSES 💰
- **Tabla BD**: `gastos`
- **Dependencias**: `viajes` ✅ + `usuarios` ✅ + `actividades` + `entradas_diario`

### FASE 10: EXPENSE_SPLITS 🧾
- **Tabla BD**: `division_gastos`
- **Dependencias**: `gastos` + `usuarios` ✅

### FASE 11: PHOTOS 📸
- **Tabla BD**: `fotos`
- **Dependencias**: `viajes` ✅ + `usuarios` ✅ + `dias` + `entradas_diario`

### FASE 12: ACTIVITY_VOTES 🗳️
- **Tabla BD**: `votos_actividad`
- **Dependencias**: `actividades` + `usuarios` ✅

### FASE 13: DIARY_RECOMMENDATIONS 💡
- **Tabla BD**: `recomendaciones_diario`
- **Dependencias**: `entradas_diario`

### FASE 14: PLAN_REALITY_DIFFERENCES 📊
- **Tabla BD**: `diferencias_plan_realidad`
- **Dependencias**: `viajes` ✅ + `dias` + `actividades`

### FASE 15: SYNC_QUEUE 🔄
- **Tabla BD**: `cola_sincronizacion`
- **Dependencias**: `usuarios` ✅ + `viajes` ✅

**Total faltantes: 10 entidades**

¿Con cuál entidad quieres que empiece? Recomiendo seguir el orden de dependencias: **DAYS** → **ACTIVITIES** → **DIARY_ENTRIES** → **EXPENSES** → etc.