from fastapi import APIRouter
from database import get_connection
from models import TicketCreate, TicketUpdate
import uuid

router = APIRouter()

@router.get("/tickets/{user_id}/{role}")
def get_tickets(user_id: str, role: str):
    conn = get_connection()
    cur = conn.cursor()

    # 🔒 Always filter by user_id (even for admin)
    cur.execute("""
        SELECT id, date, ticket_id, rest_ids, vendor_ids, status, remarks
        FROM tickets
        WHERE user_id=%s
        ORDER BY created_at DESC
    """, (user_id,))

    rows = cur.fetchall()

    result = []
    for row in rows:
        result.append({
            "id": str(row[0]),
            "date": str(row[1]),
            "ticket_id": row[2],
            "rest_ids": row[3],
            "vendor_ids": row[4],
            "status": row[5],
            "remarks": row[6]
        })

    cur.close()
    conn.close()

    return result


@router.post("/tickets")
def create_ticket(data: TicketCreate):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO tickets (
            id, user_id, date, ticket_id, rest_ids, vendor_ids, status, remarks
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        str(uuid.uuid4()),
        data.user_id,
        data.date,
        data.ticket_id,
        data.rest_ids,
        data.vendor_ids,
        data.status,
        data.remarks
    ))

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "created"}


@router.put("/tickets/{id}")
def update_ticket(id: str, data: TicketUpdate):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE tickets
        SET date=%s, ticket_id=%s, rest_ids=%s, vendor_ids=%s, status=%s, remarks=%s
        WHERE id=%s
    """, (
        data.date,
        data.ticket_id,
        data.rest_ids,
        data.vendor_ids,
        data.status,
        data.remarks,
        id
    ))

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "updated"}


@router.delete("/tickets/{id}")
def delete_ticket(id: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM tickets WHERE id=%s", (id,))

    conn.commit()
    cur.close()
    conn.close()

    return {"message": "deleted"}