from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from services.security import verify_manage_token
import logging

logger = logging.getLogger(__name__)

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in ["/docs", "/openapi.json", "/", "/health", "/subnet/status"]:
            return await call_next(request)
        token = request.headers.get("Authorization")
        if token and token.startswith("Bearer "):
            token = token[7:]
        
        if not token:
            return JSONResponse(status_code=401, content={"error": "Missing or invalid token"})
        
        user = verify_manage_token(token)
        if not user:
            return JSONResponse(status_code=401, content={"error": "Invalid token"})
        
        logger.info(f"User {user} authenticated")

        # if "node-manage" not in user.get("roles", []) :
        #     return JSONResponse(status_code=403, content={"error": "Forbidden"})
        
        return await call_next(request)