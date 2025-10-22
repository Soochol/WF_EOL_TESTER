"""
Database Manager

Handles database initialization and connection management.
"""

# Standard library imports
from pathlib import Path
from typing import Optional

# Third-party imports
from loguru import logger
from sqlalchemy import event, text
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    AsyncEngine,
    AsyncSession,
    create_async_engine,
)

# Local application imports
from infrastructure.database.schema import Base


# SQLite Foreign Key enforcement - applies to ALL connections
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """
    Enable foreign key constraints for every SQLite connection.

    SQLite disables foreign keys by default. This event listener ensures
    that EVERY connection has foreign keys enabled for referential integrity.

    Args:
        dbapi_conn: Raw DBAPI connection
        connection_record: Connection record (unused)
    """
    _ = connection_record  # Unused parameter
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class DatabaseManager:
    """Manages database connection and session lifecycle"""

    def __init__(self, database_path: str = "logs/test_data.db"):
        """
        Initialize database manager

        Args:
            database_path: Path to SQLite database file
        """
        self._database_path = Path(database_path)
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker] = None

        # Ensure directory exists
        self._database_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info(f"DatabaseManager initialized with path: {self._database_path}")

    async def initialize(self) -> None:
        """Initialize database engine and create tables with foreign key enforcement"""
        try:
            # Create async engine for SQLite
            database_url = f"sqlite+aiosqlite:///{self._database_path}"
            self._engine = create_async_engine(
                database_url,
                echo=False,  # Set to True for SQL query logging
                future=True,
            )

            # Enable foreign keys for SQLite (required for referential integrity)
            # This must be done for each connection as SQLite disables FK by default
            async with self._engine.begin() as conn:
                # Enable foreign key constraints
                await conn.execute(text("PRAGMA foreign_keys = ON"))

                # Verify foreign keys are enabled
                result = await conn.execute(text("PRAGMA foreign_keys"))
                fk_status = result.scalar()
                if fk_status == 1:
                    logger.info("Foreign key constraints ENABLED")
                else:
                    logger.warning("Foreign key constraints DISABLED (this is a problem!)")

                # Create all tables
                await conn.run_sync(Base.metadata.create_all)

            # Create session factory with foreign key enforcement
            self._session_factory = async_sessionmaker(
                self._engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )

            logger.info(f"Database initialized successfully at {self._database_path}")

        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    async def close(self) -> None:
        """Close database connection"""
        if self._engine:
            await self._engine.dispose()
            logger.info("Database connection closed")

    def get_session(self) -> AsyncSession:
        """
        Get a new database session

        Returns:
            AsyncSession instance

        Raises:
            RuntimeError: If database is not initialized
        """
        if not self._session_factory:
            raise RuntimeError("Database not initialized. Call initialize() first.")

        return self._session_factory()

    @property
    def engine(self) -> Optional[AsyncEngine]:
        """Get database engine"""
        return self._engine

    @property
    def is_initialized(self) -> bool:
        """Check if database is initialized"""
        return self._engine is not None
