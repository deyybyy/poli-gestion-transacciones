"""Agrupa todos los routers de la versión 1 de la API."""

from fastapi import APIRouter

from app.api.v1.endpoints import commerces, health, transactions

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(commerces.router)
api_router.include_router(transactions.router)
