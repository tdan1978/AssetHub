from sqlalchemy.orm import Query


def paginate(query: Query, page: int, size: int):
    total = query.count()
    items = query.offset((page - 1) * size).limit(size).all()
    return total, items
