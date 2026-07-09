from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas
from ..database import get_db
from .. import models
from ..auth_relation import get_current_user

router = APIRouter(prefix="/task", dependencies=[Depends(get_current_user)], tags=["tasks"])

# list all tasks
@router.get("/", response_model=list[schemas.EventBase])
async def list_tasks(db: Session = Depends(get_db)):
    return db.query(models.Event).all()

# register a task
@router.post("/add", response_model=schemas.EventCreate)
async def add_task(task: schemas.EventCreate, db: Session = Depends(get_db)):
    db_schedule = models.Event(
        plan_name = task.plan_name,
        start_date = task.start_date,
        finish_date = task.finish_date,
        start_time = task.start_time,
        finish_time = task.finish_time,
        alarm = task.alarm,
        repeats = task.repeats,
        tags = task.tags,
        location = task.location,
        url = task.url,
        departure = task.departure,
        departure_time = task.departure_time,
        memo = task.memo
    )
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

# show a task
@router.get("/view_task", response_model=schemas.EventBase)
async def show_task(task_id: int, db: Session = Depends(get_db)):
    db_schedule = db.query(models.Event).filter(models.Event.id == task_id).first()
    if not db_schedule:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_schedule

# update a task
@router.post("/update", response_model=schemas.EventCreate)
async def update_task(task: schemas.EventCreate, db: Session = Depends(get_db)):
    db_schedule = db.query(models.Event).filter(models.Event.id == task.id).first()
    if not db_schedule:
        raise HTTPException(status_code=404, detail="Failed to change task")

    db_schedule.plan_name = task.plan_name
    db_schedule.start_date = task.start_date
    db_schedule.finish_date = task.finish_date
    db_schedule.start_time = task.start_time
    db_schedule.finish_time = task.finish_time
    db_schedule.alarm = task.alarm
    db_schedule.repeats = task.repeats
    db_schedule.tags = task.tags
    db_schedule.location = task.location
    db_schedule.url = task.url
    db_schedule.departure = task.departure
    db_schedule.departure_time = task.departure_time
    db_schedule.memo = task.memo
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

# delete a task
@router.delete("/delete", response_model=schemas.EventBase)
async def delete_task(task_id: int, db: Session = Depends(get_db)):
    db_schedule = db.query(models.Event).filter(models.Event.id == task_id).first()
    if not db_schedule:
        raise HTTPException(status_code=404, detail="Failed to delete task")
    db.delete(db_schedule)
    db.commit()
    return db_schedule
