from datetime import date, datetime

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100), unique=True)
    phone: Mapped[str] = mapped_column(String(20))
    state: Mapped[str] = mapped_column(String(2))
    region: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column()

    policies: Mapped[list["Policy"]] = relationship(back_populates="customer")


class Policy(Base):
    __tablename__ = "policies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"))
    policy_number: Mapped[str] = mapped_column(String(20), unique=True)
    product_line: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20))
    premium: Mapped[float] = mapped_column(Float)
    deductible: Mapped[float] = mapped_column(Float)
    coverage_limit: Mapped[float] = mapped_column(Float)
    start_date: Mapped[date] = mapped_column()
    end_date: Mapped[date] = mapped_column()
    region: Mapped[str] = mapped_column(String(20))

    customer: Mapped["Customer"] = relationship(back_populates="policies")
    claims: Mapped[list["Claim"]] = relationship(back_populates="policy")
    payments: Mapped[list["Payment"]] = relationship(back_populates="policy")


class Claim(Base):
    __tablename__ = "claims"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    policy_id: Mapped[int] = mapped_column(ForeignKey("policies.id"))
    claim_number: Mapped[str] = mapped_column(String(20), unique=True)
    claim_type: Mapped[str] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(String(20))
    amount_claimed: Mapped[float] = mapped_column(Float)
    amount_paid: Mapped[float] = mapped_column(Float)
    filed_date: Mapped[date] = mapped_column()
    resolved_date: Mapped[date | None] = mapped_column(nullable=True)
    description: Mapped[str] = mapped_column(String(200))

    policy: Mapped["Policy"] = relationship(back_populates="claims")


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    policy_id: Mapped[int] = mapped_column(ForeignKey("policies.id"))
    amount: Mapped[float] = mapped_column(Float)
    payment_date: Mapped[date] = mapped_column()
    payment_method: Mapped[str] = mapped_column(String(20))
    status: Mapped[str] = mapped_column(String(20))

    policy: Mapped["Policy"] = relationship(back_populates="payments")
