from fastapi import FastAPI, HTTPException

app = FastAPI(title="Library Member Service")

members = [
    {
        "id": 1,
        "name": "Sneha",
        "email": "sneha@library.com",
        "active": True
    },
    {
        "id": 2,
        "name": "Rahul",
        "email": "rahul@library.com",
        "active": True
    },
    {
        "id": 3,
        "name": "Ananya",
        "email": "ananya@library.com",
        "active": True
    }
]


@app.get("/")
def home():
    return {"service": "Member Service", "status": "running"}


@app.get("/members")
def get_members():
    return members


@app.get("/members/{member_id}")
def get_member(member_id: int):
    for member in members:
        if member["id"] == member_id:
            return member

    raise HTTPException(status_code=404, detail="Member not found")