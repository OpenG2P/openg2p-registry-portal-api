from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class IndividualDetails(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    family_name: Optional[str] = None
    given_name: Optional[str] = None
    email: Optional[str] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    birthdate: Optional[date] = date(2000, 1, 1)
    birth_place: Optional[str] = None
    phone: Optional[str] = None
    company_id: Optional[int] = None
    registration_date: Optional[date] = date.today
    create_date: Optional[date] = datetime.utcnow
    write_date: datetime = datetime.utcnow
    is_registrant: bool = True
    is_group: bool = False
