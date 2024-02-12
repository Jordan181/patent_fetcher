from abc import ABC

from models import Patent

class PatentStoreBase(ABC):
    def store(self, patents: list[Patent]) -> None:
        raise NotImplementedError()
    
class MemoryPatentStore(PatentStoreBase):
    def __init__(self) -> None:
        self.patents = []

    def store(self, patents: list[Patent]) -> None:
        self.patents.append(patents)

class DatabasePatentStore(PatentStoreBase):
    def __init__(self,
        host: str,
        name: str,
        user: str,
        password: str,
        port: int
    ):
        self._host = host
        self._name = name
        self._user = user
        self._pass = password
        self._port = port

    def store(self, patents: list[Patent]) -> None:
        pass
    # with psycopg2.connect(host=db_host, user=db_user, password=db_pass, dbname=db_name, port=db_port) as conn:
    #     with conn.cursor() as cursor:
    #         print("Successfully made a cursor")