import os
import ssl
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional

class DatabaseConnection:
    _instance: Optional["DatabaseConnection"] = None
    _client: Optional[AsyncIOMotorClient] = None
    _database: Optional[AsyncIOMotorDatabase] = None

    def __new__(cls) -> "DatabaseConnection":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def connect(self) -> None:
        """Conectar a MongoDB Atlas con configuración SSL mejorada"""
        if self._client is None:
            mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
            database_name = os.getenv("MONGODB_DATABASE", "voyaj")
            
            # Configuración SSL para MongoDB Atlas
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Configuración de conexión optimizada para Atlas
            self._client = AsyncIOMotorClient(
                mongodb_url,
                tls=True,
                tlsAllowInvalidCertificates=True,
                tlsAllowInvalidHostnames=True,
                ssl_context=ssl_context,
                serverSelectionTimeoutMS=10000,  # 10 segundos
                connectTimeoutMS=10000,
                socketTimeoutMS=10000,
                maxPoolSize=10,
                minPoolSize=1,
                maxIdleTimeMS=30000,
                heartbeatFrequencyMS=10000,
                retryWrites=True
            )
            
            self._database = self._client[database_name]
            
            # Verificar conexión con ping más robusto
            try:
                await self._client.admin.command('ping')
                print("✅ Conexión a MongoDB Atlas establecida exitosamente")
            except Exception as e:
                print(f"❌ Error conectando a MongoDB Atlas: {e}")
                # Intentar con configuración alternativa
                await self._connect_fallback(mongodb_url, database_name)

    async def _connect_fallback(self, mongodb_url: str, database_name: str) -> None:
        """Método de conexión alternativo para casos problemáticos"""
        print("🔄 Intentando conexión alternativa...")
        
        try:
            # Configuración más permisiva
            self._client = AsyncIOMotorClient(
                mongodb_url,
                tls=True,
                tlsInsecure=True,  # Más permisivo
                serverSelectionTimeoutMS=5000,  # Timeout más corto
                connectTimeoutMS=5000,
                socketTimeoutMS=5000,
                retryWrites=True,
                w='majority'
            )
            
            self._database = self._client[database_name]
            await self._client.admin.command('ping')
            print("✅ Conexión alternativa establecida")
            
        except Exception as e:
            print(f"❌ Error en conexión alternativa: {e}")
            # Como último recurso, usar conexión sin SSL verification
            await self._connect_no_ssl_verify(mongodb_url, database_name)

    async def _connect_no_ssl_verify(self, mongodb_url: str, database_name: str) -> None:
        """Conexión sin verificación SSL (solo para desarrollo)"""
        print("🔄 Intentando conexión sin verificación SSL...")
        
        try:
            # URL modificada para deshabilitar SSL verification
            import urllib.parse
            
            # Extraer componentes de la URL
            parsed = urllib.parse.urlparse(mongodb_url)
            
            # Reconstruir URL con parámetros SSL relajados
            new_params = []
            if parsed.query:
                params = urllib.parse.parse_qs(parsed.query)
                for key, values in params.items():
                    if key not in ['ssl', 'tls', 'tlsInsecure']:
                        for value in values:
                            new_params.append(f"{key}={value}")
            
            # Agregar parámetros SSL permisivos
            new_params.extend([
                'tls=true',
                'tlsAllowInvalidCertificates=true',
                'tlsAllowInvalidHostnames=true'
            ])
            
            new_query = '&'.join(new_params)
            modified_url = urllib.parse.urlunparse((
                parsed.scheme,
                parsed.netloc,
                parsed.path,
                parsed.params,
                new_query,
                parsed.fragment
            ))
            
            self._client = AsyncIOMotorClient(
                modified_url,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000
            )
            
            self._database = self._client[database_name]
            await self._client.admin.command('ping')
            print("✅ Conexión sin verificación SSL establecida")
            
        except Exception as e:
            print(f"❌ Error final en conexión: {e}")
            print("💡 Sugerencias:")
            print("   - Verifica que la IP esté en la whitelist de MongoDB Atlas")
            print("   - Revisa las credenciales en el .env")
            print("   - Intenta actualizar pymongo: pip install --upgrade pymongo motor")
            raise e

    async def disconnect(self) -> None:
        """Desconectar de MongoDB"""
        if self._client:
            self._client.close()
            self._client = None
            self._database = None
            print("✅ Conexión a MongoDB cerrada")

    @classmethod
    def get_database(cls) -> AsyncIOMotorDatabase:
        """Obtener instancia de la base de datos"""
        instance = cls()
        if instance._database is None:
            raise RuntimeError("Base de datos no conectada. Llama a connect() primero.")
        return instance._database

    @classmethod
    async def get_client(cls) -> AsyncIOMotorClient:
        """Obtener cliente de MongoDB"""
        instance = cls()
        if instance._client is None:
            await instance.connect()
        return instance._client