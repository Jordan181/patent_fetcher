from datetime import date
from models import Patent

from stores import PatentStoreBase


class Fetcher:
    def __init__(self, stores: list[PatentStoreBase]) -> None:
        if len(stores) == 0:
            raise ValueError("At least one store must be provided.")
        
        self._stores = stores

    def fetch(self, start: date, end: date) -> list[Patent]:
        if end <= start:
            raise ValueError("End date must be greater than start date.")

        patents = self._download(start, end)
        for store in self._stores:
            store.store(patents)

        return patents

    def _download(self, start: date, end: date) -> list[Patent]:
        return [
            Patent("1", "2", "Me", date.today(), date.today(), "My invention"),
        ]