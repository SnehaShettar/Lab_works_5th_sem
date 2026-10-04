import os
import httpx

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI(title="Library Loan Service")


# These defaults are for local testing.
# Docker Compose will replace them with service names later.
BOOK_SERVICE_URL = os.getenv(
    "BOOK_SERVICE_URL",
    "http://127.0.0.1:8001"
)

MEMBER_SERVICE_URL = os.getenv(
    "MEMBER_SERVICE_URL",
    "http://127.0.0.1:8002"
)


loans = []


class BorrowRequest(BaseModel):
    book_id: int
    member_id: int


@app.get("/")
def home():
    return {
        "service": "Loan Service",
        "status": "running"
    }


@app.get("/loans")
def get_loans():
    return loans


@app.post("/loans/borrow")
async def borrow_book(request: BorrowRequest):

    # Check whether the book exists and is available
    try:
        async with httpx.AsyncClient() as client:
            book_response = await client.get(
                f"{BOOK_SERVICE_URL}/books/{request.book_id}"
            )

        if book_response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail="Book not found"
            )

        book = book_response.json()

    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Book Service unavailable"
        )

    if not book["available"]:
        raise HTTPException(
            status_code=400,
            detail="Book is not available"
        )

    # Check whether the member exists and is active
    try:
        async with httpx.AsyncClient() as client:
            member_response = await client.get(
                f"{MEMBER_SERVICE_URL}/members/{request.member_id}"
            )

        if member_response.status_code == 404:
            raise HTTPException(
                status_code=404,
                detail="Member not found"
            )

        member = member_response.json()

    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Member Service unavailable"
        )

    if not member["active"]:
        raise HTTPException(
            status_code=400,
            detail="Member is not active"
        )

    # Mark the book as unavailable
    try:
        async with httpx.AsyncClient() as client:
            availability_response = await client.put(
                f"{BOOK_SERVICE_URL}/books/{request.book_id}/availability",
                params={"available": False}
            )

        if availability_response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail="Could not update book availability"
            )

    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Book Service unavailable"
        )

    # Create the loan
    loan = {
        "loan_id": len(loans) + 1,
        "book_id": request.book_id,
        "book_title": book["title"],
        "member_id": request.member_id,
        "member_name": member["name"],
        "status": "borrowed"
    }

    loans.append(loan)

    return {
        "message": "Book borrowed successfully",
        "loan": loan
    }


@app.post("/loans/return/{loan_id}")
async def return_book(loan_id: int):

    loan = None

    for item in loans:
        if item["loan_id"] == loan_id:
            loan = item
            break

    if loan is None:
        raise HTTPException(
            status_code=404,
            detail="Loan not found"
        )

    if loan["status"] == "returned":
        raise HTTPException(
            status_code=400,
            detail="Book already returned"
        )

    # Mark the book as available again
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{BOOK_SERVICE_URL}/books/{loan['book_id']}/availability",
                params={"available": True}
            )

        if response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail="Could not update book availability"
            )

    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Book Service unavailable"
        )

    loan["status"] = "returned"

    return {
        "message": "Book returned successfully",
        "loan": loan
    }