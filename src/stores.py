from contextlib import contextmanager
import psycopg2

from abc import ABC
from datetime import date
from dataclasses import astuple
from psycopg2.extras import execute_values

from src.models import Patent


class PatentStoreBase(ABC):
    """
    Defines a base class for saving and loading patent data.
    """
    def save(self, patents: list[Patent]) -> None:
        raise NotImplementedError()
    
    def load(self, start: date, end: date) -> list[Patent]:
        raise NotImplementedError()
    
    def clear(self) -> None:
        raise NotImplementedError()
    
class MemoryPatentStore(PatentStoreBase):
    """
    Holds patent data in memory.

    In practice this store has no purpose because the lifetime of the app
    is limited to a single task, thus the store is non-persistant, but it is
    still useful for testing and debugging purposes.
    """
    def __init__(self) -> None:
        self.patents = []

    def save(self, patents: list[Patent]) -> None:
        self.patents.extend(patents)

    def load(self, start: date, end: date) -> list[Patent]:
        return [p for p in self.patents if start <= p.grant_date <= end]
    
    def clear(self) -> None:
        self.patents = []

class DatabasePatentStore(PatentStoreBase):
    """
    Connects to a postgreSQL database with schema specified in schema.sql.

    Connection logic could be extracted to support other DB servers.
    """
    def __init__(self,
        host: str,
        name: str,
        user: str,
        password: str,
        port: int
    ):
        self._connection_params = {
            "host": host,
            "user": user,
            "password": password,
            "dbname": name,
            "port": port,
        }

    def save(self, patents: list[Patent]) -> None:
        if not patents:
            return
        
        query = """
            INSERT INTO patents VALUES %s 
            ON CONFLICT (patent_number) DO NOTHING;
        """

        values = [astuple(p) for p in patents]

        with self._db_cursor() as cursor:
            execute_values(cursor, query, values)        

    def load(self, start: date, end: date) -> list[Patent]:
        query = """
            SELECT * FROM patents
            WHERE grant_date >= %s AND grant_date <= %s
        """

        with self._db_cursor() as cursor:
            cursor.execute(query, (start, end))
            return [Patent(*row) for row in cursor.fetchall()]
        
    def clear(self) -> None:
        with self._db_cursor() as cursor:
            cursor.execute("TRUNCATE patents;")
    
    @contextmanager
    def _db_cursor(self):
        with psycopg2.connect(**self._connection_params) as conn:
            with conn.cursor() as cursor:
                yield cursor