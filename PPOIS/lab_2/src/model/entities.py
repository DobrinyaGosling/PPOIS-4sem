from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PatientRecord(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: int
    patient_full_name: str = Field(min_length=1)
    address: str = Field(min_length=1)
    birth_date: date
    visit_date: date
    doctor_full_name: str = Field(min_length=1)
    conclusion: str = Field(min_length=1)


class PatientRecordCreate(BaseModel):
    patient_full_name: str = Field(min_length=1)
    address: str = Field(min_length=1)
    birth_date: date
    visit_date: date
    doctor_full_name: str = Field(min_length=1)
    conclusion: str = Field(min_length=1)


class SearchCriteria(BaseModel):
    patient_surname: Optional[str] = None
    address: Optional[str] = None
    birth_date: Optional[date] = None
    doctor_name: Optional[str] = None
    visit_date: Optional[date] = None
