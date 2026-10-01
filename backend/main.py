from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.database import engine, Base, migrate_sqlite_schema
from app.db.models import ticket_model

# 1. NEW IMPORT
from app.api.v1.routes import tickets

Base.metadata.create_all(bind=engine)
migrate_sqlite_schema()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Welcome to the AI Ticket System API"}

# 2. CONNECT THE ROUTER
app.include_router(
    tickets.router, 
    prefix=f"{settings.API_V1_STR}/tickets", 
    tags=["Tickets"]
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
