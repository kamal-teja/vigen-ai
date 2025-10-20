from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import auth, ads

app = FastAPI(
    title="Ad Video Generator API",
    description="API for generating short ad videos",
    version="1.0.0"
)

# Configure CORS
# Prepare origins list with safe fallbacks (helps when env may be empty)
origins = {origin.rstrip('/') for origin in settings.cors_origins_list if origin}

# Add permissive localhost defaults to smooth local dev across tooling
default_local_origins = {
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
}

if not origins:
    # default to localhost frontend during development
    origins = set(default_local_origins)
else:
    origins.update(default_local_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?$",
)

# Include routers
app.include_router(auth.router)
app.include_router(ads.router)


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Ad Video Generator API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
