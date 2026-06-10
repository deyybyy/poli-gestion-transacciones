"""Configuración central de la aplicación.

Las variables se cargan desde el entorno (o desde un archivo .env en
desarrollo local) usando pydantic-settings. Las variables de entorno
inyectadas por Docker Compose tienen prioridad sobre el archivo .env.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Aplicación
    app_name: str = "API Gestión de Transacciones"
    app_env: str = "development"  # development | production

    # Base de datos (MariaDB)
    db_host: str = "localhost"
    db_port: int = 3306
    db_name: str = "transacciones_db"
    db_user: str = "root"
    db_password: str = "secreto"

    @property
    def database_url(self) -> str:
        """Cadena de conexión para SQLAlchemy usando el driver PyMySQL."""
        return (
            f"mysql+pymysql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}?charset=utf8mb4"
        )


@lru_cache
def get_settings() -> Settings:
    """Devuelve una instancia cacheada de la configuración."""
    return Settings()
