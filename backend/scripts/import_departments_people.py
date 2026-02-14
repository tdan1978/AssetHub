import csv
import sys
from pathlib import Path

from app.core.database import SessionLocal
from app.models.department import Department
from app.models.person import Person


def parse_bool(value, default=True):
    if value is None:
        return default
    text = str(value).strip().lower()
    if text in ("1", "true", "yes", "y", "on", "active"):
        return True
    if text in ("0", "false", "no", "n", "off", "inactive"):
        return False
    return default


def load_csv(path):
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def ensure_departments(db, rows):
    created = 0
    updated = 0
    by_code = {}
    for dept in db.query(Department).filter(Department.is_deleted == False).all():
        if dept.code:
            by_code[dept.code] = dept

    for row in rows:
        name = (row.get("name") or "").strip()
        code = (row.get("code") or "").strip() or None
        if not name:
            continue
        existing = by_code.get(code) if code else None
        if not existing:
            existing = (
                db.query(Department)
                .filter(Department.name == name, Department.is_deleted == False)
                .first()
            )
        if not existing:
            dept = Department(
                name=name,
                code=code,
                sort_order=int(row.get("sort_order") or 0),
                is_active=parse_bool(row.get("is_active"), True),
                is_deleted=False,
            )
            db.add(dept)
            db.commit()
            db.refresh(dept)
            if code:
                by_code[code] = dept
            created += 1
        else:
            existing.name = name
            if code:
                existing.code = code
                by_code[code] = existing
            if row.get("sort_order") not in (None, ""):
                existing.sort_order = int(row.get("sort_order") or 0)
            if row.get("is_active") not in (None, ""):
                existing.is_active = parse_bool(row.get("is_active"), existing.is_active)
            db.commit()
            updated += 1

    # second pass: set parent_id based on parent_code
    for row in rows:
        code = (row.get("code") or "").strip()
        parent_code = (row.get("parent_code") or "").strip()
        if not code:
            continue
        dept = by_code.get(code)
        if not dept:
            continue
        if not parent_code:
            if dept.parent_id is not None:
                dept.parent_id = None
                db.commit()
            continue
        parent = by_code.get(parent_code)
        if parent and dept.parent_id != parent.id:
            dept.parent_id = parent.id
            db.commit()

    return created, updated


def import_people(db, rows):
    created = 0
    updated = 0
    dept_by_name = {
        d.name: d for d in db.query(Department).filter(Department.is_deleted == False).all()
    }
    for row in rows:
        name = (row.get("name") or "").strip()
        if not name:
            continue
        emp_code = (row.get("emp_code") or "").strip() or None
        dept_name = (row.get("dept") or "").strip()
        dept = dept_by_name.get(dept_name)
        phone = (row.get("phone") or "").strip() or None
        email = (row.get("email") or "").strip() or None
        status = (row.get("status") or "").strip() or None

        existing = None
        if emp_code:
            existing = (
                db.query(Person)
                .filter(Person.emp_code == emp_code, Person.is_deleted == False)
                .first()
            )
        if not existing:
            existing = (
                db.query(Person)
                .filter(Person.name == name, Person.is_deleted == False)
                .first()
            )

        if not existing:
            person = Person(
                name=name,
                emp_code=emp_code,
                dept_id=dept.id if dept else None,
                phone=phone,
                email=email,
                status=status,
                is_deleted=False,
            )
            db.add(person)
            db.commit()
            created += 1
        else:
            existing.name = name
            if emp_code:
                existing.emp_code = emp_code
            if dept:
                existing.dept_id = dept.id
            if phone is not None:
                existing.phone = phone
            if email is not None:
                existing.email = email
            if status is not None:
                existing.status = status
            db.commit()
            updated += 1

    return created, updated


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/import_departments_people.py <departments.csv> [people.csv]")
        sys.exit(1)
    with SessionLocal() as db:
        dept_created = dept_updated = None
        people_created = people_updated = None

        dept_csv = Path(sys.argv[1])
        if not dept_csv.exists():
            print("Departments CSV not found.")
            sys.exit(1)
        dept_rows = load_csv(dept_csv)
        dept_created, dept_updated = ensure_departments(db, dept_rows)

        if len(sys.argv) >= 3:
            people_csv = Path(sys.argv[2])
            if not people_csv.exists():
                print("People CSV not found.")
                sys.exit(1)
            people_rows = load_csv(people_csv)
            people_created, people_updated = import_people(db, people_rows)

    if dept_created is not None:
        print(f"Departments: created={dept_created}, updated={dept_updated}")
    if people_created is not None:
        print(f"People: created={people_created}, updated={people_updated}")


if __name__ == "__main__":
    main()
