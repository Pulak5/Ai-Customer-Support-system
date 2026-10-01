from fastapi import FastAPI
from app.core.config import settings
from app.db.database import engine, Base
from app.db.models import ticket_model

# 1. NEW IMPORT
from app.api.v1.routes import tickets

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
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