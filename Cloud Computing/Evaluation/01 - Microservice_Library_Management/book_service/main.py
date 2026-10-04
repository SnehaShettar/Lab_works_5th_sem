from fastapi import FastAPI, HTTPException

app = FastAPI(title="Library Book Service")

books = [
    {
        "id": 1,
        "title": "The Alchemist",
        "author": "Paulo Coelho",
        "available": True
    },
    {
        "id": 2,
        "title": "1984",
        "author": "George Orwell",
        "available": True
    },
    {
        "id": 3,
        "title": "Clean Code",
        "author": "Robert C. Martin",
        "available": True
    }
]


@app.get("/")
def home():
    return {"service": "Book Service", "status": "running"}


@app.get("/books")
def get_books():
    return books


@app.get("/books/{book_id}")
def get_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book

    raise HTTPException(status_code=404, detail="Book not found")


@app.put("/books/{book_id}/availability")
def update_availability(book_id: int, available: bool):
    for book in books:
        if book["id"] == book_id:
            book["available"] = available
            return book

    raise HTTPException(status_code=404, detail="Book not found")