Crear el entorno virtual:

python -m venv venv

Activar el entorno virtual:

.\venv\Scripts\activate


Instalar dependencias:

pip install -r requirements.txt


uvicorn src.main:app --reload


Analizando el estado actual del repositorio contra el plan de creación:


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


**Total faltantes: 10 entidades**

¿Con cuál entidad quieres que empiece? Recomiendo seguir el orden de dependencias: **DAYS** → **ACTIVITIES** → **DIARY_ENTRIES** → **EXPENSES** → etc.