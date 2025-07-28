
# Estados de usuario
USER_STATUS = {
    "ACTIVE": "active",
    "INACTIVE": "inactive", 
    "PENDING_VERIFICATION": "pending_verification",
    "BLOCKED": "blocked"
}

# Roles de usuario
USER_ROLES = {
    "ADMIN": "admin",
    "USER": "user"
}

# Roles de miembro de viaje
TRIP_MEMBER_ROLES = {
    "OWNER": "owner",
    "EDITOR": "editor", 
    "VIEWER": "viewer"
}

# Estados de invitación
INVITATION_STATUS = {
    "PENDING": "pendiente",
    "ACCEPTED": "aceptada",
    "REJECTED": "rechazada",
    "CANCELLED": "cancelada",
    "EXPIRED": "expirada"
}

# Estados de amistad
FRIENDSHIP_STATUS = {
    "PENDING": "pendiente",
    "ACCEPTED": "aceptada", 
    "REJECTED": "rechazada"
}

# Tipos de gastos
EXPENSE_CATEGORIES = {
    "TRANSPORT": "transport",
    "ACCOMMODATION": "accommodation",
    "FOOD": "food",
    "ENTERTAINMENT": "entertainment", 
    "SHOPPING": "shopping",
    "HEALTH": "health",
    "OTHER": "other"
}

# Monedas soportadas
SUPPORTED_CURRENCIES = [
    "USD", "EUR", "GBP", "MXN", "CAD", "AUD", "JPY", "CNY", "BRL", "ARS"
]

# Códigos de error
ERROR_CODES = {
    # Autenticación
    "INVALID_CREDENTIALS": "INVALID_CREDENTIALS",
    "TOKEN_EXPIRED": "TOKEN_EXPIRED",
    "TOKEN_INVALID": "TOKEN_INVALID",
    "TOKEN_MISSING": "TOKEN_MISSING",
    "ACCOUNT_LOCKED": "ACCOUNT_LOCKED",
    "EMAIL_NOT_VERIFIED": "EMAIL_NOT_VERIFIED",
    
    # Usuario
    "USER_NOT_FOUND": "USER_NOT_FOUND",
    "USER_ALREADY_EXISTS": "USER_ALREADY_EXISTS",
    "USER_DELETED": "USER_DELETED",
    
    # Validación
    "VALIDATION_ERROR": "VALIDATION_ERROR",
    "INVALID_EMAIL": "INVALID_EMAIL",
    "WEAK_PASSWORD": "WEAK_PASSWORD",
    
    # Sistema
    "DATABASE_ERROR": "DATABASE_ERROR",
    "INTERNAL_SERVER_ERROR": "INTERNAL_SERVER_ERROR",
    "RATE_LIMIT_EXCEEDED": "RATE_LIMIT_EXCEEDED",
    "FORBIDDEN": "FORBIDDEN",
    "NOT_FOUND": "NOT_FOUND"
}

# Límites de la aplicación
APP_LIMITS = {
    "MAX_LOGIN_ATTEMPTS": 5,
    "LOGIN_LOCK_DURATION_MINUTES": 30,
    "PASSWORD_MIN_LENGTH": 8,
    "PASSWORD_MAX_LENGTH": 128,
    "NAME_MIN_LENGTH": 2,
    "NAME_MAX_LENGTH": 100,
    "EMAIL_MAX_LENGTH": 254,
    "SEARCH_MIN_LENGTH": 2,
    "PAGINATION_DEFAULT_LIMIT": 20,
    "PAGINATION_MAX_LIMIT": 100,
    "FILE_MAX_SIZE_MB": 10,
    "JWT_EXPIRATION_HOURS": 24,
    "REFRESH_TOKEN_EXPIRATION_DAYS": 30,
    "EMAIL_VERIFICATION_EXPIRATION_HOURS": 24,
    "PASSWORD_RESET_EXPIRATION_HOURS": 1
}

# Tipos de archivos permitidos
ALLOWED_FILE_TYPES = {
    "IMAGES": ["jpg", "jpeg", "png", "gif", "webp"],
    "DOCUMENTS": ["pdf", "doc", "docx", "txt"],
    "VIDEOS": ["mp4", "avi", "mov", "wmv"],
    "AUDIO": ["mp3", "wav", "ogg"]
}

# Configuración de CORS
CORS_SETTINGS = {
    "ALLOW_ORIGINS": ["http://localhost:3000", "http://localhost:3001"],
    "ALLOW_CREDENTIALS": True,
    "ALLOW_METHODS": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "ALLOW_HEADERS": ["Content-Type", "Authorization", "X-Requested-With"]
}

# Configuración de rate limiting
RATE_LIMITS = {
    "LOGIN": {"requests": 5, "window_minutes": 15},
    "REGISTER": {"requests": 3, "window_minutes": 60},
    "PASSWORD_RESET": {"requests": 3, "window_minutes": 60},
    "EMAIL_VERIFICATION": {"requests": 3, "window_minutes": 60},
    "GENERAL": {"requests": 100, "window_minutes": 15}
}

# Tipos de eventos de dominio
EVENT_TYPES = {
    # Usuarios
    "USER_REGISTERED": "user.registered",
    "USER_EMAIL_VERIFIED": "user.email_verified", 
    "USER_LOGGED_IN": "user.logged_in",
    "USER_PASSWORD_CHANGED": "user.password_changed",
    "USER_PROFILE_UPDATED": "user.profile_updated",
    "USER_DELETED": "user.deleted",
    
    # Amistades
    "FRIEND_REQUEST_SENT": "friendship.request_sent",
    "FRIEND_REQUEST_ACCEPTED": "friendship.request_accepted",
    "FRIEND_REQUEST_REJECTED": "friendship.request_rejected",
    "FRIENDSHIP_REMOVED": "friendship.removed",
    
    # Viajes
    "TRIP_CREATED": "trip.created",
    "TRIP_UPDATED": "trip.updated",
    "TRIP_MEMBER_ADDED": "trip.member_added",
    "TRIP_MEMBER_REMOVED": "trip.member_removed",
    
    # Notificaciones
    "NOTIFICATION_SENT": "notification.sent",
    "NOTIFICATION_READ": "notification.read"
}