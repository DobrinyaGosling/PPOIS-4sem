from datetime import date

from sqlalchemy import Date, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=False)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    visit_date: Mapped[date] = mapped_column(Date, nullable=False)
    doctor_full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    conclusion: Mapped[str] = mapped_column(Text, nullable=False)
