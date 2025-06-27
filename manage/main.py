from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.config import settings
from manage.router import stake, wallet
from manage.middlewares.auth import AuthMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.security import HTTPBearer
import logging

logging.basicConfig(level=settings.MANAGER_DEBUG)

app = FastAPI(
    title="Subnet Manager",
    version="0.1.0",
    description="Subnet Manager",
    openapi_url="/openapi.json"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(AuthMiddleware)

# Include routers
app.include_router(stake.router)
app.include_router(wallet.router)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    # apply BearerAuth globally
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method.setdefault("security", [{"BearerAuth": []}])
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


@app.get("/")
async def root():
    return {
        "version": "0.1.0",
    }

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "manage.main:app",
        host=settings.MANAGER_HOST,
        port=settings.MANAGER_PORT,
        log_level=settings.MANAGER_DEBUG.lower(),
        reload=settings.MANAGER_RELOAD
    ) 