from datetime import date as Date

from pydantic import BaseModel, Field


# =========================================
# TRIP SCHEMAS
# =========================================

class TripCreate(BaseModel):
    trip_name: str
    destination: str
    start_date: Date
    end_date: Date
    members: list[str]


class TripResponse(BaseModel):
    id: str
    trip_name: str
    destination: str
    start_date: Date
    end_date: Date
    members: list[str]


# =========================================
# EXPENSE CREATE
# =========================================

class ExpenseCreate(BaseModel):
    title: str

    amount: float = Field(
        gt=0,
        description="Expense amount must be greater than 0"
    )

    category: str
    paid_by: str
    shared_by: list[str]

    date: Date

    description: str | None = None


# =========================================
# EXPENSE UPDATE
# =========================================

class ExpenseUpdate(BaseModel):

    title: str | None = None

    amount: float | None = Field(
        default=None,
        gt=0
    )

    category: str | None = None

    paid_by: str | None = None

    shared_by: list[str] | None = None

    # IMPORTANT:
    # Use Date instead of date here
    date: Date | None = None

    description: str | None = None


# =========================================
# EXPENSE RESPONSE
# =========================================

class ExpenseResponse(BaseModel):
    id: str
    trip_id: str

    title: str
    amount: float
    category: str
    paid_by: str
    shared_by: list[str]

    individual_share: float

    date: Date

    description: str | None = None


# =========================================
# MEMBER SUMMARY
# =========================================

class MemberSummary(BaseModel):
    name: str

    paid: float
    share: float
    balance: float

    amount_owed: float
    amount_to_receive: float


# =========================================
# TRIP SUMMARY
# =========================================

class TripSummaryResponse(BaseModel):
    trip_id: str

    total_expenses: float

    members: list[MemberSummary]


# =========================================
# GENERAL MESSAGE
# =========================================

class MessageResponse(BaseModel):
    message: str