from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from .database import engine, Base
from .routers import (
    auth, pos_terminals, transactions, reconciliation, 
    reports, uploads, users, audit
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="POS Reconciliation Dashboard",
    description="A comprehensive dashboard for reconciling Bank and POS transactions",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(pos_terminals.router, prefix="/api/pos-terminals", tags=["POS Terminals"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["Transactions"])
app.include_router(reconciliation.router, prefix="/api/reconciliation", tags=["Reconciliation"])
app.include_router(uploads.router, prefix="/api/uploads", tags=["Data Upload"])
app.include_router(reports.router, prefix="/api/reports", tags=["Reports"])
app.include_router(audit.router, prefix="/api/audit", tags=["Audit Trail"])

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return {"message": "POS Reconciliation Dashboard API"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}