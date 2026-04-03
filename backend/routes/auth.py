from fastapi import APIRouter
from database import get_connection
from models import LoginModel

router = APIRouter()

@router.post("/login")
def login(data: LoginModel):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, employee_id, name, role 
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
        "employee_id": user[1],
        "name": user[2],
        "role": user[3]
    }