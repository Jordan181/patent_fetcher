from dataclasses import dataclass, is_dataclass, asdict
from datetime import date
from json import JSONEncoder


@dataclass
class Patent:
    patent_number: str
    patent_application_number: str
    assignee_entity_name: str
    filing_date: date
    grant_date: date
    invention_title: str

class DataclassJSONEncoder(JSONEncoder):
    def default(self, o):
        if is_dataclass(o):
            return asdict(o)
        if isinstance(o, date):
            return o.isoformat()
        return super().default(o)