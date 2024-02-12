from dataclasses import dataclass
from datetime import date


@dataclass
class Patent:
    patent_number: str
    patent_application_number: str
    assignee_entity_name: str
    filing_date: date
    grant_date: date
    invention_title: str
