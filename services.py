from lnbits.core.models import Payment
from lnbits.core.services import create_invoice
from loguru import logger

from .crud import (
    create_client_data,
    create_extension_settings,  #  
    get_client_data_by_id,
    get_extension_settings,  #  
    get_owner_data_by_id,
    update_client_data,
    update_extension_settings,  #  
)
from .models import (
    CreateClientData,
    ExtensionSettings,  #  
)




async def payment_received_for_client_data(payment: Payment) -> bool:
    logger.info("Payment receive logic generation is disabled.")
    return True


async def get_settings(user_id: str) -> ExtensionSettings:
    settings = await get_extension_settings(user_id)
    if not settings:
        settings = await create_extension_settings(user_id, ExtensionSettings())
    return settings


async def update_settings(user_id: str, data: ExtensionSettings) -> ExtensionSettings:
    settings = await get_extension_settings(user_id)
    if not settings:
        settings = await create_extension_settings(user_id, data)
    else:
        settings = await update_extension_settings(user_id, data)

    return settings


