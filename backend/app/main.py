from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import Session

from .database import engine, init_db
from .routers import drinks, events, fines, ledger, lineups, subscriptions, ticker, users
from .seed import seed


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    with Session(engine) as session:
        seed(session)
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="Vereins-App API", lifespan=lifespan)
    app.include_router(users.router)
    app.include_router(events.router)
    app.include_router(drinks.router)
    app.include_router(ledger.router)
    app.include_router(fines.router)
    app.include_router(lineups.router)
    app.include_router(ticker.router)
    app.include_router(subscriptions.router)
    return app


app = create_app()
