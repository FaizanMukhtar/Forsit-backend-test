from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import engine, Base, get_db
from .routers import sales, inventory, products

Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="E-commerce Admin API (Forsit Test)",
    description="API for e-commerce admin dashboard (Forsit Test)",
    version="0.1.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(sales.router)
app.include_router(inventory.router)
app.include_router(products.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to E-commerce Admin API (Forsit Test)"}

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}