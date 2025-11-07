import asyncio

from fastapi import APIRouter
from lnbits.tasks import create_permanent_unique_task
from loguru import logger

from .crud import db, get_startup_enabled_ssh_tunnels
from .tasks import wait_for_paid_invoices
from .views import lnbits_cloud_connect_generic_router
from .views_api import lnbits_cloud_connect_api_router

# Initialize SSH service
try:
    from .ssh_service import tunnel_manager
    logger.info("SSH tunnel manager initialized")
except Exception as e:
    logger.warning(f"SSH tunnel manager initialization failed: {e}")

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
    
    # Stop all SSH tunnels on extension shutdown
    try:
        from .ssh_service import tunnel_manager
        asyncio.run(tunnel_manager.stop_all_tunnels())
        logger.info("All SSH tunnels stopped")
    except Exception as ex:
        logger.warning(f"Error stopping SSH tunnels: {ex}")


def lnbits_cloud_connect_start():
    startup_task = create_permanent_unique_task("ext_lnbits_cloud_connect_startup", start_startup_tunnels)
    scheduled_tasks.append(startup_task)


async def start_startup_tunnels():
    """
    Start all SSH tunnels marked for startup.
    """
    try:
        from .ssh_service import tunnel_manager
        
        startup_tunnels = await get_startup_enabled_ssh_tunnels()
        logger.info(f"Found {len(startup_tunnels)} tunnels marked for startup")
        
        for tunnel in startup_tunnels:
            try:
                success = await tunnel_manager.start_tunnel(tunnel)
                if success:
                    logger.info(f"Successfully started startup tunnel: {tunnel.name} ({tunnel.id})")
                else:
                    logger.error(f"Failed to start startup tunnel: {tunnel.name} ({tunnel.id})")
            except Exception as e:
                logger.error(f"Error starting startup tunnel {tunnel.name} ({tunnel.id}): {e}")
                
    except Exception as e:
        logger.error(f"Error in startup tunnel initialization: {e}")


__all__ = [
    "db",
    "lnbits_cloud_connect_ext",
    "lnbits_cloud_connect_start",
    "lnbits_cloud_connect_static_files",
    "lnbits_cloud_connect_stop",
]