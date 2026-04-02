from fastapi import APIRouter
from database import get_connection
from models import LoginModel

router = APIRouter()

@router.post("/login")
def login(data: LoginModel):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, name, role 
        FROM users 
        WHERE employee_id=%s AND password=%s
    """, (data.employee_id, data.password))

    user = cur.fetchone()

    cur.close()
    conn.close()

    if not user:
        return {"error": "Invalid credentials"}

    return {
        "id": str(user[0]),
        "name": user[1],
        "role": user[2]
    }