from bson import ObjectId
from fastapi import HTTPException

from database import (
    get_trip_collection,
    get_expense_collection
)

from schemas import (
    TripCreate,
    ExpenseCreate,
    ExpenseUpdate
)


# =========================================
# HELPER
# =========================================

def validate_object_id(value: str):

    if not ObjectId.is_valid(value):
        raise HTTPException(
            status_code=400,
            detail="Invalid ID"
        )

    return ObjectId(value)


# =========================================
# TRIP HELPER
# =========================================

def trip_helper(trip: dict):

    return {
        "id": str(trip["_id"]),
        "trip_name": trip["trip_name"],
        "destination": trip["destination"],
        "start_date": trip["start_date"],
        "end_date": trip["end_date"],
        "members": trip["members"]
    }


# =========================================
# CREATE TRIP
# =========================================

def create_trip(trip: TripCreate):

    collection = get_trip_collection()

    if trip.end_date < trip.start_date:
        raise HTTPException(
            status_code=400,
            detail="End date cannot be before start date"
        )

    if not trip.members:
        raise HTTPException(
            status_code=400,
            detail="At least one member is required"
        )

    members = list(dict.fromkeys(trip.members))

    trip_data = trip.model_dump(
        mode="json"
    )

    trip_data["members"] = members

    result = collection.insert_one(
        trip_data
    )

    return {
        "id": str(result.inserted_id),
        "trip_name": trip_data["trip_name"],
        "destination": trip_data["destination"],
        "start_date": trip_data["start_date"],
        "end_date": trip_data["end_date"],
        "members": trip_data["members"]
    }


# =========================================
# GET TRIP
# =========================================

def get_trip(trip_id: str):

    collection = get_trip_collection()

    object_id = validate_object_id(
        trip_id
    )

    trip = collection.find_one(
        {"_id": object_id}
    )

    if not trip:
        raise HTTPException(
            status_code=404,
            detail="Trip not found"
        )

    return trip_helper(trip)


# =========================================
# EXPENSE HELPER
# =========================================

def expense_helper(expense: dict):

    shared_by = expense.get(
        "shared_by",
        []
    )

    amount = float(
        expense["amount"]
    )

    if shared_by:
        individual_share = (
            amount / len(shared_by)
        )
    else:
        individual_share = 0

    return {
        "id": str(expense["_id"]),
        "trip_id": str(expense["trip_id"]),
        "title": expense["title"],
        "amount": amount,
        "category": expense["category"],
        "paid_by": expense["paid_by"],
        "shared_by": shared_by,
        "individual_share": round(
            individual_share,
            2
        ),
        "date": expense["date"],
        "description": expense.get(
            "description"
        )
    }


# =========================================
# CREATE EXPENSE
# =========================================

def create_expense(
    trip_id: str,
    expense: ExpenseCreate
):

    trip_object_id = validate_object_id(
        trip_id
    )

    trip_collection = get_trip_collection()
    expense_collection = get_expense_collection()

    trip = trip_collection.find_one(
        {"_id": trip_object_id}
    )

    if not trip:
        raise HTTPException(
            status_code=404,
            detail="Trip not found"
        )

    if expense.paid_by not in trip["members"]:
        raise HTTPException(
            status_code=400,
            detail="Paid-by member is not part of the trip"
        )

    if not expense.shared_by:
        raise HTTPException(
            status_code=400,
            detail="shared_by cannot be empty"
        )

    shared_by = list(
        dict.fromkeys(
            expense.shared_by
        )
    )

    for member in shared_by:

        if member not in trip["members"]:
            raise HTTPException(
                status_code=400,
                detail=f"{member} is not part of the trip"
            )

    expense_data = expense.model_dump(
        mode="json"
    )

    expense_data["trip_id"] = trip_object_id
    expense_data["shared_by"] = shared_by

    expense_data["individual_share"] = round(
        expense.amount / len(shared_by),
        2
    )

    result = expense_collection.insert_one(
        expense_data
    )

    return {
        "id": str(result.inserted_id),
        "trip_id": trip_id,
        "title": expense_data["title"],
        "amount": expense_data["amount"],
        "category": expense_data["category"],
        "paid_by": expense_data["paid_by"],
        "shared_by": expense_data["shared_by"],
        "individual_share": expense_data["individual_share"],
        "date": expense_data["date"],
        "description": expense_data.get("description")
    }


# =========================================
# GET EXPENSES
# =========================================

def get_expenses(
    trip_id: str,
    category: str | None = None,
    paid_by: str | None = None,
    min_amount: float | None = None,
    max_amount: float | None = None,
    sort_by: str | None = None
):

    trip_object_id = validate_object_id(
        trip_id
    )

    trip_collection = get_trip_collection()

    trip = trip_collection.find_one(
        {"_id": trip_object_id}
    )

    if not trip:
        raise HTTPException(
            status_code=404,
            detail="Trip not found"
        )

    expense_collection = get_expense_collection()

    query = {
        "trip_id": trip_object_id
    }

    if category:
        query["category"] = category

    if paid_by:
        query["paid_by"] = paid_by

    if min_amount is not None:
        query.setdefault(
            "amount",
            {}
        )
        query["amount"]["$gte"] = min_amount

    if max_amount is not None:
        query.setdefault(
            "amount",
            {}
        )
        query["amount"]["$lte"] = max_amount

    cursor = expense_collection.find(
        query
    )

    if sort_by == "amount":
        cursor = cursor.sort(
            "amount",
            1
        )

    elif sort_by == "date":
        cursor = cursor.sort(
            "date",
            1
        )

    return [
        expense_helper(expense)
        for expense in cursor
    ]


# =========================================
# GET EXPENSE
# =========================================

def get_expense(
    expense_id: str
):

    collection = get_expense_collection()

    object_id = validate_object_id(
        expense_id
    )

    expense = collection.find_one(
        {"_id": object_id}
    )

    if not expense:
        raise HTTPException(
            status_code=404,
            detail="Expense not found"
        )

    return expense_helper(
        expense
    )


# =========================================
# UPDATE EXPENSE
# =========================================

def update_expense(
    expense_id: str,
    expense_data: ExpenseUpdate
):

    collection = get_expense_collection()

    object_id = validate_object_id(
        expense_id
    )

    existing_expense = collection.find_one(
        {"_id": object_id}
    )

    if not existing_expense:
        raise HTTPException(
            status_code=404,
            detail="Expense not found"
        )

    updated_data = expense_data.model_dump(
        mode="json",
        exclude_none=True
    )

    if not updated_data:
        return expense_helper(
            existing_expense
        )

    trip_collection = get_trip_collection()

    trip = trip_collection.find_one(
        {
            "_id": existing_expense["trip_id"]
        }
    )

    if not trip:
        raise HTTPException(
            status_code=404,
            detail="Trip not found"
        )

    # Validate paid_by
    if "paid_by" in updated_data:

        if updated_data["paid_by"] not in trip["members"]:

            raise HTTPException(
                status_code=400,
                detail="Paid-by member is not part of the trip"
            )

    # Validate shared_by
    if "shared_by" in updated_data:

        if not updated_data["shared_by"]:

            raise HTTPException(
                status_code=400,
                detail="shared_by cannot be empty"
            )

        updated_data["shared_by"] = list(
            dict.fromkeys(
                updated_data["shared_by"]
            )
        )

        for member in updated_data["shared_by"]:

            if member not in trip["members"]:

                raise HTTPException(
                    status_code=400,
                    detail=f"{member} is not part of the trip"
                )

    # Calculate share
    amount = updated_data.get(
        "amount",
        existing_expense["amount"]
    )

    shared_by = updated_data.get(
        "shared_by",
        existing_expense["shared_by"]
    )

    if not shared_by:

        raise HTTPException(
            status_code=400,
            detail="shared_by cannot be empty"
        )

    updated_data["individual_share"] = round(
        amount / len(shared_by),
        2
    )

    collection.update_one(
        {"_id": object_id},
        {
            "$set": updated_data
        }
    )

    updated_expense = collection.find_one(
        {"_id": object_id}
    )

    return expense_helper(
        updated_expense
    )


# =========================================
# DELETE EXPENSE
# =========================================

def delete_expense(
    expense_id: str
):

    collection = get_expense_collection()

    object_id = validate_object_id(
        expense_id
    )

    result = collection.delete_one(
        {"_id": object_id}
    )

    if result.deleted_count == 0:

        raise HTTPException(
            status_code=404,
            detail="Expense not found"
        )

    return {
        "message": "Expense deleted successfully"
    }


# =========================================
# TRIP SUMMARY
# =========================================

def get_trip_summary(
    trip_id: str
):

    trip_object_id = validate_object_id(
        trip_id
    )

    trip_collection = get_trip_collection()
    expense_collection = get_expense_collection()

    trip = trip_collection.find_one(
        {"_id": trip_object_id}
    )

    if not trip:
        raise HTTPException(
            status_code=404,
            detail="Trip not found"
        )

    members = trip["members"]

    summary = {}

    for member in members:

        summary[member] = {
            "name": member,
            "paid": 0,
            "share": 0,
            "balance": 0,
            "amount_owed": 0,
            "amount_to_receive": 0
        }

    expenses = expense_collection.find(
        {
            "trip_id": trip_object_id
        }
    )

    total_expenses = 0

    for expense in expenses:

        amount = float(
            expense["amount"]
        )

        paid_by = expense["paid_by"]

        shared_by = expense.get(
            "shared_by",
            []
        )

        total_expenses += amount

        if not shared_by:
            continue

        individual_share = (
            amount / len(shared_by)
        )

        summary[paid_by]["paid"] += amount

        for member in shared_by:

            summary[member]["share"] += (
                individual_share
            )

    for member in members:

        paid = summary[member]["paid"]
        share = summary[member]["share"]

        balance = paid - share

        summary[member]["paid"] = round(
            paid,
            2
        )

        summary[member]["share"] = round(
            share,
            2
        )

        summary[member]["balance"] = round(
            balance,
            2
        )

        if balance > 0:

            summary[member]["amount_to_receive"] = round(
                balance,
                2
            )

        elif balance < 0:

            summary[member]["amount_owed"] = round(
                abs(balance),
                2
            )

    return {
        "trip_id": trip_id,
        "total_expenses": round(
            total_expenses,
            2
        ),
        "members": list(
            summary.values()
        )
    }