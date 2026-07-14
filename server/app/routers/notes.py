from fastapi import APIRouter, HTTPException, Depends
from app.db.sqlalchemy import get_db
from sqlalchemy.orm import Session
from app.schemas.notes import CreateNote, NoteResponse
from app.models.notes import Note
from sqlalchemy import select, or_, update, delete, func

from app.services.redis import (
   redis_set,
   redis_get,
   redis_delete,
   redis_ttl
)

router = APIRouter(prefix="/notes", tags=["Notes"])

@router.post("/")
async def create_note(note: CreateNote, db: Session = Depends(get_db)):
    if not note.title or not note.content:
        raise HTTPException(status_code=400, detail="both field are required")
   
    try:
        
        new_note = Note(title=note.title, content=note.content)
        db.add(new_note)
        await db.commit()
        await db.refresh(new_note)
        return {"message": "Note created successfully"}
    except Exception as e:
        ## rollback 
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def get_notes(db: Session = Depends(get_db)):
    try:
        ## Redis services get value
        redis_notes = await redis_get(f"redis_note")
        note_expireIn = await redis_ttl(f"redis_note")
        if redis_notes:
            return {"notes": redis_notes, "expire_in": note_expireIn}

        ### to filter by desc() and limit 10 of them
        stml = (
            select(Note)
             .order_by(Note.create_at.desc())
             .limit(10)
        )

        ### to filter by search match
        # stml = (
        #     select(Note)
        #     .where(or_(Note.content.ilike("%bro%"), Note.title.ilike("%bro%")))
        #     .limit(10)
        # )

        result = await db.execute(stml)
        notes = result.scalars().all()

        ## converting ORM response Note to dict type
        note_response = [NoteResponse.model_validate(note) for note in notes]

        ## Redis services set value
        await redis_set(f"redis_note", note_response, 200)

        return note_response
    except Exception as e:
        ## rollback 
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{note_id}")
async def update_note(note_id: int, note: CreateNote, db: Session = Depends(get_db)):
    if not note_id:
        raise HTTPException(status_code=400, detail="note_id is required")
    if not note.title or not note.content:
        raise HTTPException(status_code=400, detail="both field are required")

    try:
        stml = update(Note).where(Note.id == note_id).values(title=note.title, content=note.content)
        await db.execute(stml)
        await db.commit()
        return {"message": "Note updated successfully"}
    except Exception as e:
        ## rollback 
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{note_id}")
async def delete_note(note_id: int, db: Session = Depends(get_db)):
    if not note_id:
        raise HTTPException(status_code=400, detail="note_id is required")
    try:
        stml = delete(Note).where(Note.id == note_id)
        await db.execute(stml)
        await db.commit()
        return {"message": "Note deleted successfully"}
    except Exception as e:
        ## rollback 
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search")
async def oprate_notes(db: Session = Depends(get_db)):
    try:
        # stml = (
        #     select(
        #         func.count(Note.id),
        #         func.max(Note.create_at),
        #         func.min(Note.create_at),
        #     )
        #     .where(Note.title.like("%hi%"))
        # )
        # result = await db.execute(stml)
        # total_user, max_create_at, min_create_at = result.one()
        # return {
        #     "total_user": total_user,
        #     "max_create_at": max_create_at,
        #     "min_create_at": min_create_at,
        # }  

        ### group by
        stml = (
            select(
                Note.create_at,
                func.count(Note.id)
            )
            .group_by(Note.create_at)
        )
        result = await db.execute(stml)
        notes = result.all()
        return notes     
    except Exception as e:
        ## rollback 
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))