from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine
from app.routers import auth, assets, asset_fields, licenses, users, roles, stocktakes, dashboard, categories, maintenance

app = FastAPI(title="ITAM")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"] ,
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "ITAM API"}


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(roles.router)
app.include_router(assets.router)
app.include_router(asset_fields.router)
app.include_router(licenses.router)
app.include_router(maintenance.router)
app.include_router(stocktakes.router)
app.include_router(dashboard.router)
app.include_router(categories.router)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
