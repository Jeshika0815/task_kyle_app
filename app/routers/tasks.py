from app.routers.prompt_organize import token_veri
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas
from ..database import get_db
from .. import models
from ..auth_relation import get_http_client

router = APIRouter(prefix="/task", dependencies=[Depends(token_veri)], tags=["tasks"])

# list all tasks
@router.get("/", response_model=list[schemas.EventBase])
async def list_tasks(db: Session = Depends(get_db)):
    return db.query(models.Event).all()

# register a task
@router.post("/add", response_model=schemas.EventCreate)
async def add_task(task: schemas.EventCreate, db: Session = Depends(get_db)):
    db_schedule = models.Event(
        plan_name = task.plan_name,
        date = task.date,
        time = task.time,
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
    if db_schedule:
        return db_schedule
    else:
        raise HTTPException(status_code=500, detail="Failed to add task")

# show a task
@router.get("/view_task", response_model=schemas.EventBase)
async def show_task(task_id: int, db: Session = Depends(get_db)):
    return db.query(models.Event).filter(models.Event.task_id == task_id).first()

# update a task
@router.post("/update", response_model=schemas.EventCreate)
async def update_task(task: schemas.EventCreate, db: Session = Depends(get_db)):
    db_schedule = db.query(models.Event).filter(models.Event.task_id == task.task_id).first()
    if db_schedule:
        db_schedule.plan_name = task.plan_name
        db_schedule.date = task.date
        db_schedule.time = task.time
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

    if db_schedule:
        return db_schedule
    else:
        raise HTTPException(status_code=404, detail="Failed to change task")

# delete a task
@router.delete("/delete", response_model=schemas.EventBase)
async def delete_task(task: schemas.EventBase, db: Session = Depends(get_db)):
    db_schedule = db.query(models.Event).filter(models.Event.task_id == task.task_id).first()
    if db_schedule:
        db.delete(db_schedule)
        db.commit()
        return db_schedule
    else:
        raise HTTPException(status_code=404, detail="Failed to delete task")
