CREATE TABLE patents (
    patent_number               text PRIMARY KEY,
    patent_application_number   text,
    assignee_entity_name        text,
    filing_date                 date,
    grant_date                  date,
    invention_title             text
)