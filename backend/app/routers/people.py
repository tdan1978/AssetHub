from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.database import get_db
from app.core.deps import require_permission
from app.models.person import Person
from app.schemas.common import Message, Page
from app.schemas.person import PersonCreate, PersonOut, PersonUpdate
from app.utils.pagination import paginate

router = APIRouter(prefix="/api/v1/people", tags=["people"])


@router.get("", response_model=Page[PersonOut])
def list_people(
    page: int = 1,
    size: int = 50,
    q: str | None = None,
    dept_id: int | None = None,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("people", "view")),
):
    query = db.query(Person).filter(Person.is_deleted == False)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(Person.name.like(like), Person.emp_code.like(like)))
    if dept_id:
        query = query.filter(Person.dept_id == dept_id)
    total, items = paginate(query.order_by(Person.id.desc()), page, size)
    return Page(total=total, items=items)


@router.get("/options")
def list_people_options(
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("people", "view")),
):
    items = (
        db.query(Person.id, Person.name)
        .filter(Person.is_deleted == False)
        .order_by(Person.id.desc())
        .all()
    )
    return [{"value": item.id, "label": item.name} for item in items]


@router.get("/{person_id}", response_model=PersonOut)
def get_person(
    person_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("people", "view")),
):
    item = db.query(Person).filter(Person.id == person_id, Person.is_deleted == False).first()
    if not item:
        raise HTTPException(status_code=404, detail="Person not found")
    return item


@router.post("", response_model=PersonOut)
def create_person(
    payload: PersonCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("people", "create")),
):
    item = Person(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/{person_id}", response_model=PersonOut)
def update_person(
    person_id: int,
    payload: PersonUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("people", "update")),
):
    item = db.query(Person).filter(Person.id == person_id, Person.is_deleted == False).first()
    if not item:
        raise HTTPException(status_code=404, detail="Person not found")
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{person_id}", response_model=Message)
def delete_person(
    person_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("people", "delete")),
):
    item = db.query(Person).filter(Person.id == person_id, Person.is_deleted == False).first()
    if not item:
        raise HTTPException(status_code=404, detail="Person not found")
    item.is_deleted = True
    db.commit()
    return Message(message="Deleted")
