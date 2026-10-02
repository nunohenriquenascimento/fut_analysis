from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.exception_handlers import request_validation_exception_handler
from sqlalchemy.exc import OperationalError

from app.api import router
from app.live_api import router as live_router
from app.statistics_api import router as statistics_router
from app.config import get_settings
from app.auth_api import router as auth_router
from app.live_socket import router as socket_router
from app.auth_debug import middleware as auth_debug_middleware

app = FastAPI(title="CCDR Vila Cortez do Mondego — Sub-19", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE"],
    allow_headers=["Content-Type", "X-CSRF-Token", "X-Requested-With"],
    expose_headers=["X-Request-ID"],
)
app.include_router(auth_router)
app.include_router(router)
app.include_router(live_router)
app.include_router(statistics_router)
app.include_router(socket_router)
app.middleware("http")(auth_debug_middleware)


@app.middleware("http")
async def private_responses(request: Request, call_next):
    response = await call_next(request)
    if request.url.path != "/health":
        response.headers["Cache-Control"] = "no-store"
    return response


@app.exception_handler(RequestValidationError)
async def safe_validation_errors(request: Request, exc: RequestValidationError):
    if request.url.path.startswith(("/auth/", "/users")):
        return JSONResponse(status_code=422, content={"detail": [
            {key: error[key] for key in ("loc", "msg", "type") if key in error} for error in exc.errors()
        ]})
    return await request_validation_exception_handler(request, exc)


@app.exception_handler(OperationalError)
async def database_unavailable(request: Request, exc: OperationalError) -> JSONResponse:
    # Do not return connection strings or database internals to clients.
    return JSONResponse(status_code=503, content={"detail": "Base de dados indisponível."})
