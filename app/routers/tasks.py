from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import schemas
from ..database import get_db
from .. import models
from ..auth_relation import auth_verification
from .. import calender_relation
from datetime import datetime, timedelta

router = APIRouter(prefix="/task", tags=["tasks"])

# Sync with Google Calendar
@router.post("/sync")
def sync_gcalendar(current_user: models.Users = Depends(auth_verification)):
    if not calender_relation.is_connected(current_user):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You are not connected to Google Calendar")
    service = calender_relation.build_calendar_service(current_user)
    return service

# list all tasks
@router.get("/", response_model=list[schemas.EventCreate])
async def list_tasks(db: Session = Depends(get_db), current_user: models.Users = Depends(auth_verification)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, details="You are not authenticated yet")
    return db.query(models.Events).filter(models.Events.user_id == current_user.id).all()

# register a task
@router.post("/add", response_model=schemas.EventCreate)
async def add_task(task: schemas.Plans, db: Session = Depends(get_db), current_user: models.Users = Depends(auth_verification)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authenticated yet")
    db_schedule = models.Events(
        user_id = current_user.id,
        plan_name = task.plan_name,
        start_date = task.date.start_date,
        finish_date = task.date.finish_date,
        start_time = task.time.start_time,
        finish_time = task.time.finish_time,
        alarm = task.alarm,
        repeats = task.repeats,
        tags = task.tags,
        location = task.location,
        url = task.url,
        memo = task.memo,
    )
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    if calender_relation.is_connected(current_user):
        try:
            db_schedule.google_event_id = calender_relation.add_event(current_user, db_schedule)
        except Exception:
            pass
        try:
            db_schedule.departure = calender_relation.calc_departures(current_user, db_schedule)
        except Exception:
            pass

        db.commit()
    if db_schedule:
        return db_schedule
    else:
        raise HTTPException(status_code=500, detail="Failed to add task")

# show a task
@router.get("/view_task", response_model=schemas.EventCreate)
async def show_task(task_id: int, db: Session = Depends(get_db), current_user: models.Users = Depends(auth_verification)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authenticated yet")
    return db.query(models.Events).filter(models.Events.id == task_id, models.Events.user_id == current_user.id).first()

# update a task
@router.post("/update", response_model=schemas.EventCreate)
async def update_task(task: schemas.EventCreate, db: Session = Depends(get_db), current_user: models.Users = Depends(auth_verification)):
    db_schedule = db.query(models.Events).filter(models.Events.id == task.id, models.Events.user_id == current_user.id).first()
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authenticated yet")
    if not db_schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    if db_schedule:
        db_schedule.plan_name = task.plan_name
        db_schedule.start_date = task.date.start_date
        db_schedule.finish_date = task.date.finish_date
        db_schedule.start_time = task.time.start_time
        db_schedule.finish_time = task.time.finish_time
        db_schedule.alarm = task.alarm
        db_schedule.repeats = task.repeats
        db_schedule.tags = task.tags
        db_schedule.location = task.location
        db_schedule.url = task.url
        db_schedule.memo = task.memo
        db.commit()
        db.refresh(db_schedule)

    if calender_relation.is_connected(current_user):
        try:
            calender_relation.update_event(current_user, db_schedule)
        except Exception:
            pass

        try:
            db_schedule.departure = calender_relation.calc_departures(current_user, db_schedule)
        except Exception:
            pass
        db.commit()

    if db_schedule:
        return db_schedule
    else:
        raise HTTPException(status_code=404, detail="Failed to change task")

# delete a task
@router.delete("/delete", response_model=schemas.EventCreate)
async def delete_task(task: schemas.EventCreate, db: Session = Depends(get_db), current_user: models.Users = Depends(auth_verification)):
    db_schedule = db.query(models.Events).filter(models.Events.id == task.id, models.Events.user_id == current_user.id).first()
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authenticated yet")
    if not db_schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    if calender_relation.is_connected(current_user):
        try:
            calender_relation.delete_event(current_user, db_schedule)
        except Exception:
            pass

    if db_schedule:
        db.delete(db_schedule)
        db.commit()
        return db_schedule
    else:
        raise HTTPException(status_code=404, detail="Failed to delete task")

# name to id(For discord only)
@router.get("/nti", response_model=int)
async def nti(plan_name: str, db: Session = Depends(get_db), current_user: models.Users = Depends(auth_verification)):
    event = models.Events
    get_schedule = db.query(event).filter(event.plan_name == plan_name, event.user_id == current_user.id).first()
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="You are not authenticated yet")
    if not get_schedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    search_id = get_schedule.id
    return search_id

# For departures
@router.get("/departure", response_model=list[schemas.EventCreate])
async def due_tasks(db: Session = Depends(get_db), current_user: models.Users = Depends(auth_verification)):
    event = models.Events
    now = datetime.now()
    return (db.query(event).filter(event.user_id == current_user.id, event.departure_check == False, event.departure <= now).all())

@router.post("/departure/{task_id}/ack")
async def ack_departure(task_id: int, db: Session = Depends(get_db), current_user: models.Users = Depends(auth_verification)):
    event = models.Events
    db_event = db.query(event).filter(event.id == task_id, event.user_id == current_user.id).first()
    if not db_event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    db_event.departure_check = True
    db.commit()
    return {"ok": True}
