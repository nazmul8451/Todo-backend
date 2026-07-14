from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, todos

# Automatically create tables in SQLite on application startup
# For production projects with migration requirements, Alembic should be used instead
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TODO App with Authentication",
    description="A structured FastAPI backend with JWT user authentication and Todo CRUD endpoints",
    version="1.0.0"
)

# Set up CORS Middleware (Configure appropriately for production environments)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(todos.router)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to the FastAPI TODO API!",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }
