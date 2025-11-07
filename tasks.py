import asyncio

from lnbits.core.models import Payment
from lnbits.tasks import register_invoice_listener
from loguru import logger

from .services import payment_received_for_client_data
from .crud import get_all_ssh_tunnels, get_connected_ssh_tunnels
from .ssh_service import tunnel_manager

#######################################
########## RUN YOUR TASKS HERE ########
#######################################

# The usual task is to listen to invoices related to this extension


async def wait_for_paid_invoices():
    invoice_queue = asyncio.Queue()
    register_invoice_listener(invoice_queue, "ext_lnbits_cloud_connect")
    
    # Start SSH tunnel monitoring in parallel
    asyncio.create_task(monitor_ssh_tunnels())
    asyncio.create_task(restart_auto_reconnect_tunnels())
    
    while True:
        payment = await invoice_queue.get()
        await on_invoice_paid(payment)


# Do somethhing when an invoice related top this extension is paid


async def on_invoice_paid(payment: Payment) -> None:
    if payment.extra.get("tag") != "lnbits_cloud_connect":
        return

    logger.info(f"Invoice paid for lnbits_cloud_connect: {payment.payment_hash}")

    try:
        await payment_received_for_client_data(payment)
    except Exception as e:
        logger.error(f"Error processing payment for lnbits_cloud_connect: {e}")


#######################################
######### SSH TUNNEL MONITORING #######
#######################################

async def monitor_ssh_tunnels():
    """
    Monitor SSH tunnel health and sync database state with actual process state.
    """
    while True:
        try:
            await asyncio.sleep(60)  # Check every minute
            
            # Get all tunnels marked as connected in the database
            connected_tunnels = await get_connected_ssh_tunnels()
            active_tunnel_ids = await tunnel_manager.get_all_active_tunnels()
            
            for tunnel in connected_tunnels:
                if tunnel.id not in active_tunnel_ids:
                    logger.warning(f"Tunnel {tunnel.id} marked as connected but no active process found")
                    # The tunnel manager will handle auto-reconnection if enabled
                    
        except Exception as e:
            logger.error(f"Error in SSH tunnel monitoring: {e}")


async def restart_auto_reconnect_tunnels():
    """
    Restart tunnels that should be connected but are not active.
    This handles extension restarts and ensures auto-reconnect tunnels are restored.
    """
    try:
        await asyncio.sleep(30)  # Wait for extension to fully initialize
        
        # Get all tunnels that were connected before restart
        all_tunnels = await get_all_ssh_tunnels()
        active_tunnel_ids = await tunnel_manager.get_all_active_tunnels()
        
        for tunnel in all_tunnels:
            if tunnel.is_connected and tunnel.auto_reconnect and tunnel.id not in active_tunnel_ids:
                logger.info(f"Restarting auto-reconnect tunnel {tunnel.id}: {tunnel.name}")
                try:
                    success = await tunnel_manager.start_tunnel(tunnel)
                    if success:
                        logger.info(f"Successfully restarted tunnel {tunnel.id}")
                    else:
                        logger.error(f"Failed to restart tunnel {tunnel.id}")
                except Exception as e:
                    logger.error(f"Error restarting tunnel {tunnel.id}: {e}")
                    
                # Add delay between tunnel starts to avoid overwhelming the system
                await asyncio.sleep(5)
                
    except Exception as e:
        logger.error(f"Error in auto-reconnect tunnel startup: {e}")