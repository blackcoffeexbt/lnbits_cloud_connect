import asyncio

from fastapi import APIRouter
from lnbits.tasks import create_permanent_unique_task
from loguru import logger

from .crud import db
from .tasks import wait_for_paid_invoices
from .views import lnbits_cloud_connect_generic_router
from .views_api import lnbits_cloud_connect_api_router

lnbits_cloud_connect_ext: APIRouter = APIRouter(
    prefix="/lnbits_cloud_connect", tags=["LNbits Cloud Connect"]
)
lnbits_cloud_connect_ext.include_router(lnbits_cloud_connect_generic_router)
lnbits_cloud_connect_ext.include_router(lnbits_cloud_connect_api_router)


lnbits_cloud_connect_static_files = [
    {
        "path": "/lnbits_cloud_connect/static",
        "name": "lnbits_cloud_connect_static",
    }
]

scheduled_tasks: list[asyncio.Task] = []


def lnbits_cloud_connect_stop():
    for task in scheduled_tasks:
        try:
            task.cancel()
        except Exception as ex:
            logger.warning(ex)


def lnbits_cloud_connect_start():
    task = create_permanent_unique_task("ext_lnbits_cloud_connect", wait_for_paid_invoices)
    scheduled_tasks.append(task)


__all__ = [
    "db",
    "lnbits_cloud_connect_ext",
    "lnbits_cloud_connect_start",
    "lnbits_cloud_connect_static_files",
    "lnbits_cloud_connect_stop",
]