from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError

from app.api import router
from app.live_api import router as live_router
from app.statistics_api import router as statistics_router
from app.config import get_settings

app = FastAPI(title="CCDR Vila Cortez do Mondego — Sub-19", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE"],
    allow_headers=["Content-Type"],
)
app.include_router(router)
app.include_router(live_router)
app.include_router(statistics_router)


@app.exception_handler(OperationalError)
async def database_unavailable(request: Request, exc: OperationalError) -> JSONResponse:
    # Do not return connection strings or database internals to clients.
    return JSONResponse(status_code=503, content={"detail": "Base de dados indisponível."})
