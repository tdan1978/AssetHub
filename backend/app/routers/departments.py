from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import require_permission
from app.models.department import Department
from app.models.person import Person
from app.schemas.common import Message, Page
from app.schemas.department import DepartmentCreate, DepartmentOut, DepartmentTreeOut, DepartmentUpdate
from app.utils.pagination import paginate

router = APIRouter(prefix="/api/v1/departments", tags=["departments"])


def build_tree(items: list[Department]) -> list[DepartmentTreeOut]:
    node_map = {}
    for item in items:
        node_map[item.id] = DepartmentTreeOut(
            id=item.id,
            name=item.name,
            code=item.code,
            parent_id=item.parent_id,
            sort_order=item.sort_order,
            is_active=item.is_active,
            children=[]
        )
    roots = []
    for item in items:
        node = node_map[item.id]
        if item.parent_id and item.parent_id in node_map:
            node_map[item.parent_id].children.append(node)
        else:
            roots.append(node)
    return roots


@router.get("", response_model=Page[DepartmentOut])
def list_departments(
    page: int = 1,
    size: int = 50,
    q: str | None = None,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("departments", "view")),
):
    query = db.query(Department).filter(Department.is_deleted == False)
    if q:
        like = f"%{q}%"
        query = query.filter(Department.name.like(like))
    total, items = paginate(query.order_by(Department.sort_order.asc(), Department.id.asc()), page, size)
    return Page(total=total, items=items)


@router.get("/tree", response_model=list[DepartmentTreeOut])
def list_departments_tree(
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("departments", "view")),
):
    items = (
        db.query(Department)
        .filter(Department.is_deleted == False)
        .order_by(Department.sort_order.asc(), Department.id.asc())
        .all()
    )
    return build_tree(items)


@router.get("/options")
def list_department_options(
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("departments", "view")),
):
    items = (
        db.query(Department.id, Department.name)
        .filter(Department.is_deleted == False, Department.is_active == True)
        .order_by(Department.sort_order.asc(), Department.id.asc())
        .all()
    )
    return [{"value": item.id, "label": item.name} for item in items]


@router.get("/{dept_id}", response_model=DepartmentOut)
def get_department(
    dept_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("departments", "view")),
):
    item = db.query(Department).filter(Department.id == dept_id, Department.is_deleted == False).first()
    if not item:
        raise HTTPException(status_code=404, detail="Department not found")
    return item


@router.post("", response_model=DepartmentOut)
def create_department(
    payload: DepartmentCreate,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("departments", "create")),
):
    exists = (
        db.query(Department)
        .filter(Department.name == payload.name, Department.is_deleted == False)
        .first()
    )
    if exists:
        raise HTTPException(status_code=400, detail="Department already exists")
    item = Department(**payload.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.put("/{dept_id}", response_model=DepartmentOut)
def update_department(
    dept_id: int,
    payload: DepartmentUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("departments", "update")),
):
    item = db.query(Department).filter(Department.id == dept_id, Department.is_deleted == False).first()
    if not item:
        raise HTTPException(status_code=404, detail="Department not found")
    data = payload.model_dump(exclude_unset=True)
    if "parent_id" in data and data["parent_id"] == item.id:
        raise HTTPException(status_code=400, detail="Invalid parent")
    for key, value in data.items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{dept_id}", response_model=Message)
def delete_department(
    dept_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(require_permission("departments", "delete")),
):
    item = db.query(Department).filter(Department.id == dept_id, Department.is_deleted == False).first()
    if not item:
        raise HTTPException(status_code=404, detail="Department not found")
    child_exists = (
        db.query(Department)
        .filter(Department.parent_id == dept_id, Department.is_deleted == False)
        .first()
    )
    if child_exists:
        raise HTTPException(status_code=400, detail="Department has children")
    person_exists = (
        db.query(Person)
        .filter(Person.dept_id == dept_id, Person.is_deleted == False)
        .first()
    )
    if person_exists:
        raise HTTPException(status_code=400, detail="Department has people")
    db.delete(item)
    db.commit()
    return Message(message="Deleted")
