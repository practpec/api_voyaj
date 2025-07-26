import os
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
        """Conectar a MongoDB"""
        if self._client is None:
            mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
            database_name = os.getenv("MONGODB_DATABASE", "voyaj")
            
            self._client = AsyncIOMotorClient(mongodb_url)
            self._database = self._client[database_name]
            
            # Verificar conexión
            await self._client.admin.command('ping')

    async def disconnect(self) -> None:
        """Desconectar de MongoDB"""
        if self._client:
            self._client.close()
            self._client = None
            self._database = None

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