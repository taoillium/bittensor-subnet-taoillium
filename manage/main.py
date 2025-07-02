from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from services.config import settings
from manage.router import wallet, subnet
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
app.include_router(wallet.router)
app.include_router(subnet.router)

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
    
    # Enhanced startup information
    print("=" * 60)
    print("🚀 Starting Unified Taoillium Server")
    print("=" * 60)
    print(f"📍 Host: {settings.MANAGER_HOST}")
    print(f"🔌 Port: {settings.MANAGER_PORT}")
    print(f"🐛 Debug Level: {settings.MANAGER_DEBUG}")
    print(f"🔄 Auto Reload: {settings.MANAGER_RELOAD}")
    print(f"🌐 Network: {settings.CHAIN_NETWORK}")
    print(f"📡 NetUID: {settings.CHAIN_NETUID}")
    
    print("\n📋 Available endpoints:")
    print("  🔐 /wallet/* - Wallet management endpoints")
    print("  🌐 /subnet/* - Subnet API endpoints")
    print("  📚 /docs - Interactive API documentation")
    print("  ❤️  /health - Health check")
    print("  🏠 / - Root endpoint")
    
    print("\n🔗 Quick access:")
    print(f"  📚 API Docs: http://{settings.MANAGER_HOST}:{settings.MANAGER_PORT}/docs")
    print(f"  ❤️  Health: http://{settings.MANAGER_HOST}:{settings.MANAGER_PORT}/health")
    print(f"  🌐 Subnet Health: http://{settings.MANAGER_HOST}:{settings.MANAGER_PORT}/subnet/health")
    print("=" * 60)
    
    try:
        uvicorn.run(
            "manage.main:app",
            host=settings.MANAGER_HOST,
            port=settings.MANAGER_PORT,
            log_level=settings.MANAGER_DEBUG.lower(),
            reload=settings.MANAGER_RELOAD
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Server failed to start: {e}")
        raise 