from fastapi import APIRouter
from database import get_connection
from ws_manager import manager
from models import TicketCreate, TicketUpdate
import uuid
from typing import List
import json

router = APIRouter()

@router.get("/tickets/{user_id}/{role}")
def get_tickets(user_id: str, role: str):
    conn = get_connection()
    cur = conn.cursor()

    # 🔒 Always filter by user_id (even for admin)
    cur.execute("""
        SELECT id, date, ticket_id, rest_ids, vendor_ids, status, remarks, aggregators
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
            "rest_ids": row[3] if row[3] else [],
            "vendor_ids": row[4] if row[4] else [],
            "status": row[5],
            "remarks": row[6] if row[6] else [],
            "aggregators": row[7] if isinstance(row[7], list) else (json.loads(row[7]) if row[7] else [])
        })

    cur.close()
    conn.close()

    return result


@router.post("/tickets")
async def create_ticket(data: TicketCreate):
    print("Received data:", data.dict())
    
    conn = get_connection()
    cur = conn.cursor()

    new_id = str(uuid.uuid4())

    cur.execute("""
        INSERT INTO tickets (id, user_id, date, ticket_id, rest_ids, vendor_ids, status, remarks, aggregators)
        VALUES (%s, %s::uuid, %s, %s, %s, %s, %s, %s, %s)
    """, (
        new_id,
        data.user_id,
        data.date,
        data.ticket_id,
        data.rest_ids,
        data.vendor_ids,
        data.status,
        data.remarks,
        json.dumps([a.dict() for a in data.aggregators] if data.aggregators else [])
    ))

    conn.commit()
    print("Inserted ticket with id:", new_id, "user_id:", data.user_id)
    cur.close()
    conn.close()

    await manager.broadcast("tickets_updated")

    return {"message": "created", "id": new_id}


@router.put("/tickets/{id}")
async def update_ticket(id: str, data: TicketUpdate):
    conn = get_connection()
    cur = conn.cursor()

    update_fields = []
    values = []

    if data.date is not None:
        update_fields.append("date=%s")
        values.append(data.date)

    if data.ticket_id is not None:
        update_fields.append("ticket_id=%s")
        values.append(data.ticket_id)

    if data.rest_ids is not None:
        update_fields.append("rest_ids=%s")
        values.append(data.rest_ids)

    if data.vendor_ids is not None:
        update_fields.append("vendor_ids=%s")
        values.append(data.vendor_ids)

    if data.status is not None:
        update_fields.append("status=%s")
        values.append(data.status)

    if data.aggregators is not None:
        update_fields.append("aggregators=%s")
        values.append(json.dumps([a.dict() for a in data.aggregators]))
    
    if data.remarks is not None:
        update_fields.append("remarks=%s")
        values.append(data.remarks)

    if not update_fields:
        return {"message": "No fields to update"}

    values.append(id)

    query = f"""
        UPDATE tickets
        SET {', '.join(update_fields)}
        WHERE id=%s
    """

    cur.execute(query, tuple(values))
    conn.commit()

    cur.close()
    conn.close()
    await manager.broadcast("tickets_updated")
    return {"message": "updated"}   


@router.delete("/tickets/{id}")
async def delete_ticket(id: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM tickets WHERE id=%s", (id,))

    conn.commit()
    cur.close()
    conn.close()
    await manager.broadcast("tickets_updated")
    return {"message": "deleted"}

@router.post("/tickets/bulk")
async def bulk_upload(data: List[TicketCreate]):
    conn = get_connection()
    cur = conn.cursor()

    for d in data:
        cur.execute("""
            INSERT INTO tickets (
                id, user_id, date, ticket_id,
                rest_ids, vendor_ids, status, remarks,
                aggregators
            )
            VALUES (%s, %s::uuid, %s, %s, %s, %s, %s, %s, %s)
        """, (
            str(uuid.uuid4()),
            d.user_id,
            d.date,
            d.ticket_id,
            d.rest_ids,
            d.vendor_ids,
            d.status,
            d.remarks,
            json.dumps([a.dict() for a in d.aggregators] if d.aggregators else [])
        ))

    conn.commit()
    cur.close()
    conn.close()

    await manager.broadcast("tickets_updated")

    return {"message": "bulk upload success"}