from datetime import date, datetime, time
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from app.db.session import SessionLocal
from app.models.timetable import TimetableSlot, LessonSession, LessonStatus
from app.core.security import require_roles, get_current_user
from app.services.audit import log_event

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------- Schemas ----------

class SlotCreate(BaseModel):
    classroom_id: int
    subject_id: int
    teacher_id: Optional[int] = None
    day_of_week: int = Field(..., ge=1, le=7)
    period: Optional[int] = Field(default=None, ge=1)
    start_time: str
    end_time: str

class SlotOut(BaseModel):
    id: int
    classroom_id: int
    subject_id: int
    teacher_id: Optional[int]
    day_of_week: int
    period: Optional[int]
    start_time: str
    end_time: str
    class Config:
        from_attributes = True

class SessionStart(BaseModel):
    classroom_id: int
    subject_id: int
    teacher_id: Optional[int] = None
    date: date
    start_ts: Optional[datetime] = None
    notes: Optional[str] = None

class SessionEnd(BaseModel):
    end_ts: Optional[datetime] = None
    notes: Optional[str] = None

class SessionOut(BaseModel):
    id: int
    classroom_id: int
    subject_id: int
    teacher_id: Optional[int]
    date: date
    start_ts: datetime
    end_ts: Optional[datetime]
    status: str
    notes: Optional[str]
    class Config:
        from_attributes = True


# ---------- Timetable Slots (RBAC: admin/teacher) ----------

@router.post("/slots", response_model=SlotOut, dependencies=[Depends(require_roles("admin", "teacher"))])
def create_slot(payload: SlotCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    try:
        st = time.fromisoformat(payload.start_time)
        et = time.fromisoformat(payload.end_time)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid time format")

    if et <= st:
        raise HTTPException(status_code=422, detail="end_time must be after start_time")

    exists = db.execute(
        select(TimetableSlot).where(
            and_(
                TimetableSlot.classroom_id == payload.classroom_id,
                TimetableSlot.day_of_week == payload.day_of_week,
                TimetableSlot.start_time == st,
            )
        )
    ).scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=409, detail="Slot already exists at that time")

    slot = TimetableSlot(
        classroom_id=payload.classroom_id,
        subject_id=payload.subject_id,
        teacher_id=payload.teacher_id,
        day_of_week=payload.day_of_week,
        period=payload.period,
        start_time=st,
        end_time=et,
    )
    db.add(slot)
    db.commit()
    db.refresh(slot)

    log_event(
        db,
        actor=user["sub"],
        action="timetable.slot.create",
        obj_type="TimetableSlot",
        obj_id=slot.id,
        meta={"classroom_id": slot.classroom_id, "day_of_week": slot.day_of_week, "start": payload.start_time},
    )

    return SlotOut(
        id=slot.id,
        classroom_id=slot.classroom_id,
        subject_id=slot.subject_id,
        teacher_id=slot.teacher_id,
        day_of_week=slot.day_of_week,
        period=slot.period,
        start_time=slot.start_time.strftime("%H:%M"),
        end_time=slot.end_time.strftime("%H:%M"),
    )

@router.get("/slots", response_model=List[SlotOut], dependencies=[Depends(require_roles("admin", "teacher", "parent", "student"))])
def list_slots(classroom_id: int, day_of_week: Optional[int] = None,
               db: Session = Depends(get_db), user=Depends(get_current_user)):
    stmt = select(TimetableSlot).where(TimetableSlot.classroom_id == classroom_id)
    if day_of_week:
        stmt = stmt.where(TimetableSlot.day_of_week == day_of_week)
    slots = db.execute(stmt.order_by(TimetableSlot.day_of_week, TimetableSlot.start_time)).scalars().all()
    return [
        SlotOut(
            id=s.id,
            classroom_id=s.classroom_id,
            subject_id=s.subject_id,
            teacher_id=s.teacher_id,
            day_of_week=s.day_of_week,
            period=s.period,
            start_time=s.start_time.strftime("%H:%M"),
            end_time=s.end_time.strftime("%H:%M"),
        ) for s in slots
    ]

# ---------- Lesson Sessions (RBAC: admin/teacher) ----------

@router.post("/sessions/start", response_model=SessionOut, dependencies=[Depends(require_roles("admin", "teacher"))])
def start_session(payload: SessionStart, db: Session = Depends(get_db), user=Depends(get_current_user)):
    open_existing = db.execute(
        select(LessonSession).where(
            and_(
                LessonSession.classroom_id == payload.classroom_id,
                LessonSession.date == payload.date,
                LessonSession.status.in_([LessonStatus.in_class, LessonStatus.paused]),
            )
        )
    ).scalar_one_or_none()
    if open_existing:
        raise HTTPException(status_code=409, detail="Open session already exists")

    now = datetime.utcnow()
    session = LessonSession(
        classroom_id=payload.classroom_id,
        subject_id=payload.subject_id,
        teacher_id=payload.teacher_id,
        date=payload.date,
        start_ts=payload.start_ts or now,
        status=LessonStatus.in_class,
        notes=payload.notes,
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    log_event(
        db,
        actor=user["sub"],
        action="timetable.session.start",
        obj_type="LessonSession",
        obj_id=session.id,
        meta={"classroom_id": session.classroom_id, "date": str(session.date)},
    )

    return session

@router.post("/sessions/{session_id}/end", response_model=SessionOut, dependencies=[Depends(require_roles("admin", "teacher"))])
def end_session(session_id: int, data: SessionEnd, db: Session = Depends(get_db), user=Depends(get_current_user)):
    sess = db.get(LessonSession, session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    if sess.status not in [LessonStatus.in_class, LessonStatus.paused]:
        raise HTTPException(status_code=409, detail=f"Cannot end session in status {sess.status}")
    sess.end_ts = data.end_ts or datetime.utcnow()
    sess.status = LessonStatus.finished
    if data.notes:
        sess.notes = (sess.notes or "") + (f"\n{data.notes}" if sess.notes else data.notes)
    db.commit()
    db.refresh(sess)

    log_event(
        db,
        actor=user["sub"],
        action="timetable.session.end",
        obj_type="LessonSession",
        obj_id=sess.id,
        meta={"classroom_id": sess.classroom_id},
    )

    return sess

@router.get("/sessions/{session_id}", response_model=SessionOut, dependencies=[Depends(require_roles("admin", "teacher", "parent", "student"))])
def get_session(session_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    sess = db.get(LessonSession, session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    return sess

@router.get("/sessions/day", response_model=List[SessionOut], dependencies=[Depends(require_roles("admin", "teacher", "parent", "student"))])
def sessions_for_day(classroom_id: int, date_: date, db: Session = Depends(get_db), user=Depends(get_current_user)):
    stmt = select(LessonSession).where(
        and_(
            LessonSession.classroom_id == classroom_id,
            LessonSession.date == date_,
        )
    ).order_by(LessonSession.start_ts)
    return list(db.execute(stmt).scalars())
