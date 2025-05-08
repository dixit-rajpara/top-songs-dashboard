"""
PostgreSQL database interface for the Top Songs application.
"""
from typing import Any, Dict, List, Optional
import asyncpg
from asyncpg.pool import Pool
from pydantic import ValidationError
from top_songs.core.config import settings


class PostgresInterface:
    """Interface for PostgreSQL database operations.
    
    This class provides a high-level interface for interacting with PostgreSQL
    using asyncpg. It handles connection pooling and provides methods for 
    common database operations.
    """
    
    def __init__(self, connection_string: Optional[str] = None, 
                 min_connections: Optional[int] = None,
                 max_connections: Optional[int] = None):
        """
        Initialize the PostgreSQL interface with connection parameters.
        
        Args:
            connection_string: PostgreSQL connection string. If None, uses settings.
            min_connections: Minimum connections in the pool. If None, uses settings.
            max_connections: Maximum connections in the pool. If None, uses settings.
        """
        if settings is None or settings.postgres is None:
            if connection_string is None:
                raise ValueError("No PostgreSQL connection settings provided")
            self.connection_string = connection_string
            self.min_connections = min_connections or 1
            self.max_connections = max_connections or 10
        else:
            self.connection_string = connection_string or str(settings.postgres.postgres_dsn)
            self.min_connections = min_connections or settings.postgres.min_connections
            self.max_connections = max_connections or settings.postgres.max_connections
        
        self._pool: Optional[Pool] = None
    
    async def connect(self) -> None:
        """Create and initialize the connection pool."""
        if self._pool is not None:
            return
        
        self._pool = await asyncpg.create_pool(
            dsn=self.connection_string,
            min_size=self.min_connections,
            max_size=self.max_connections
        )
    
    async def disconnect(self) -> None:
        """Close all connections in the pool."""
        if self._pool is not None:
            await self._pool.close()
            self._pool = None
    
    async def execute(self, query: str, *args: Any) -> str:
        """
        Execute a query that doesn't return rows.
        
        Args:
            query: SQL query to execute
            *args: Query parameters
            
        Returns:
            Status tag string (e.g., "INSERT 0 1")
        """
        if self._pool is None:
            await self.connect()
        
        async with self._pool.acquire() as conn:
            return await conn.execute(query, *args)
    
    async def fetch(self, query: str, *args: Any) -> List[asyncpg.Record]:
        """
        Execute a query and return all results.
        
        Args:
            query: SQL query to execute
            *args: Query parameters
            
        Returns:
            List of records
        """
        if self._pool is None:
            await self.connect()
        
        async with self._pool.acquire() as conn:
            return await conn.fetch(query, *args)
    
    async def fetchrow(self, query: str, *args: Any) -> Optional[asyncpg.Record]:
        """
        Execute a query and return the first row.
        
        Args:
            query: SQL query to execute
            *args: Query parameters
            
        Returns:
            First record or None if no records returned
        """
        if self._pool is None:
            await self.connect()
        
        async with self._pool.acquire() as conn:
            return await conn.fetchrow(query, *args)
    
    async def fetchval(self, query: str, *args: Any) -> Any:
        """
        Execute a query and return a single value.
        
        Args:
            query: SQL query to execute
            *args: Query parameters
            
        Returns:
            First value of first record, or None if no records returned
        """
        if self._pool is None:
            await self.connect()
        
        async with self._pool.acquire() as conn:
            return await conn.fetchval(query, *args)
    
    async def transaction(self):
        """
        Start a transaction. Usage:
        
        async with db.transaction() as conn:
            await conn.execute(...)
            
        Returns:
            Transaction context manager
        """
        if self._pool is None:
            await self.connect()
        
        return self._pool.acquire()
    
    # Higher-level methods specific to the Top Songs application
    
    async def insert_top_songs_hourly(self, region: str, timestamp: str, 
                                     song_id: str, artist: str, title: str, 
                                     plays: int) -> None:
        """
        Insert or update a record in the top_songs_hourly table.
        
        Args:
            region: Geographic region code
            timestamp: ISO timestamp for the hour
            song_id: Unique identifier for the song
            artist: Artist name
            title: Song title
            plays: Number of plays
        """
        query = """
        INSERT INTO top_songs_hourly(region, timestamp, song_id, artist, title, plays)
        VALUES($1, $2, $3, $4, $5, $6)
        ON CONFLICT (region, timestamp, song_id) 
        DO UPDATE SET plays = $6
        """
        await self.execute(query, region, timestamp, song_id, artist, title, plays)
    
    async def insert_top_songs_daily(self, region: str, date: str, 
                                    song_id: str, artist: str, title: str, 
                                    plays: int) -> None:
        """
        Insert or update a record in the top_songs_daily table.
        
        Args:
            region: Geographic region code
            date: ISO date string (YYYY-MM-DD)
            song_id: Unique identifier for the song
            artist: Artist name
            title: Song title
            plays: Number of plays
        """
        query = """
        INSERT INTO top_songs_daily(region, date, song_id, artist, title, plays)
        VALUES($1, $2, $3, $4, $5, $6)
        ON CONFLICT (region, date, song_id) 
        DO UPDATE SET plays = $6
        """
        await self.execute(query, region, date, song_id, artist, title, plays)
    
    async def get_top_songs_hourly(self, region: str, timestamp: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the top songs for a specific region and hour.
        
        Args:
            region: Geographic region code
            timestamp: ISO timestamp for the hour
            limit: Maximum number of songs to return
            
        Returns:
            List of song records
        """
        query = """
        SELECT song_id, artist, title, plays
        FROM top_songs_hourly
        WHERE region = $1 AND timestamp = $2
        ORDER BY plays DESC
        LIMIT $3
        """
        rows = await self.fetch(query, region, timestamp, limit)
        return [dict(row) for row in rows]
    
    async def get_top_songs_daily(self, region: str, date: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the top songs for a specific region and day.
        
        Args:
            region: Geographic region code
            date: ISO date string (YYYY-MM-DD)
            limit: Maximum number of songs to return
            
        Returns:
            List of song records
        """
        query = """
        SELECT song_id, artist, title, plays
        FROM top_songs_daily
        WHERE region = $1 AND date = $2
        ORDER BY plays DESC
        LIMIT $3
        """
        rows = await self.fetch(query, region, date, limit)
        return [dict(row) for row in rows]
    
    async def get_regions(self) -> List[str]:
        """
        Get a list of all regions in the database.
        
        Returns:
            List of region codes
        """
        query = """
        SELECT DISTINCT region FROM top_songs_hourly
        UNION
        SELECT DISTINCT region FROM top_songs_daily
        """
        rows = await self.fetch(query)
        return [row['region'] for row in rows]


# Create a singleton instance for convenient import
postgres_db = None
try:
    if settings and settings.postgres:
        postgres_db = PostgresInterface()
except (ImportError, ValidationError):
    # Will be initialized later when settings are available
    pass 