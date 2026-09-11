from fastapi import (
    APIRouter,
    status,
    Query
)

import services

from schemas import (
    TripCreate,
    TripResponse,
    ExpenseCreate,
    ExpenseResponse,
    ExpenseUpdate,
    TripSummaryResponse,
    MessageResponse
)


router = APIRouter(
    tags=["Travel Expense Tracker"]
)


# =========================================
# CREATE TRIP
# =========================================

@router.post(
    "/trips",
    response_model=TripResponse,
    status_code=status.HTTP_201_CREATED
)
def create_trip(trip: TripCreate):

    return services.create_trip(trip)


# =========================================
# GET TRIP
# =========================================

@router.get(
    "/trips/{trip_id}",
    response_model=TripResponse
)
def get_trip(trip_id: str):

    return services.get_trip(trip_id)


# =========================================
# CREATE EXPENSE
# =========================================

@router.post(
    "/trips/{trip_id}/expenses",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED
)
def create_expense(
    trip_id: str,
    expense: ExpenseCreate
):

    return services.create_expense(
        trip_id,
        expense
    )


# =========================================
# GET EXPENSES
# =========================================

@router.get(
    "/trips/{trip_id}/expenses",
    response_model=list[ExpenseResponse]
)
def get_expenses(
    trip_id: str,

    category: str | None = Query(
        default=None
    ),

    paid_by: str | None = Query(
        default=None
    ),

    min_amount: float | None = Query(
        default=None,
        gt=0
    ),

    max_amount: float | None = Query(
        default=None,
        gt=0
    ),

    sort_by: str | None = Query(
        default=None,
        pattern="^(amount|date)$"
    )
):

    return services.get_expenses(
        trip_id=trip_id,
        category=category,
        paid_by=paid_by,
        min_amount=min_amount,
        max_amount=max_amount,
        sort_by=sort_by
    )


# =========================================
# GET EXPENSE
# =========================================

@router.get(
    "/expenses/{expense_id}",
    response_model=ExpenseResponse
)
def get_expense(expense_id: str):

    return services.get_expense(
        expense_id
    )


# =========================================
# UPDATE EXPENSE
# =========================================

@router.put(
    "/expenses/{expense_id}",
    response_model=ExpenseResponse
)
def update_expense(
    expense_id: str,
    expense: ExpenseUpdate
):

    return services.update_expense(
        expense_id,
        expense
    )


# =========================================
# DELETE EXPENSE
# =========================================

@router.delete(
    "/expenses/{expense_id}",
    response_model=MessageResponse
)
def delete_expense(expense_id: str):

    return services.delete_expense(
        expense_id
    )


# =========================================
# TRIP SUMMARY
# =========================================

@router.get(
    "/trips/{trip_id}/summary",
    response_model=TripSummaryResponse
)
def trip_summary(trip_id: str):

    return services.get_trip_summary(
        trip_id
    )