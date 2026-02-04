"""API service entrypoint (FastAPI).

This module wires core routers and dependency injection for the Algo Trading Bot Manager.
"""
from fastapi import FastAPI
from services.api.routers import bots, portfolio, backtests, regimes, data, deploy

app = FastAPI(title="Algo Trading Bot Manager API", version="0.1.0")

app.include_router(bots.router, prefix="/bots", tags=["bots"])
app.include_router(portfolio.router, prefix="/portfolio", tags=["portfolio"])
app.include_router(backtests.router, prefix="/backtests", tags=["backtests"])
app.include_router(regimes.router, prefix="/regimes", tags=["regimes"])
app.include_router(data.router, prefix="/data", tags=["data"])
app.include_router(deploy.router, prefix="/deploy", tags=["deploy"])
