# Description: This file contains the extensions API endpoints.
from http import HTTPStatus

from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from lnbits.core.models import SimpleStatus, User
from lnbits.db import Filters, Page
from lnbits.decorators import (
    check_user_exists,
    parse_filters,
)
from lnbits.helpers import generate_filter_params_openapi

from .crud import (
    create_client_data,
    create_owner_data,
    create_ssh_tunnel,
    delete_client_data,
    delete_owner_data,
    delete_ssh_tunnel,
    get_client_data_by_id,
    get_client_data_paginated,
    get_owner_data,
    get_owner_data_ids_by_user,
    get_owner_data_paginated,
    get_ssh_tunnel,
    get_ssh_tunnels_paginated,
    update_client_data,
    update_owner_data,
    update_ssh_tunnel,
)
from .models import (
    ClientData,
    ClientDataFilters,
    CreateClientData,
    CreateOwnerData,
    CreateSSHTunnel,
    ExtensionSettings,  #  
    OwnerData,
    OwnerDataFilters,
    SSHTunnel,
    SSHTunnelFilters,
)

from .services import (
    get_settings,  #  
    update_settings,  #  
)


owner_data_filters = parse_filters(OwnerDataFilters)
client_data_filters = parse_filters(ClientDataFilters)
ssh_tunnel_filters = parse_filters(SSHTunnelFilters)

lnbits_cloud_connect_api_router = APIRouter()


############################# Owner Data #############################
@lnbits_cloud_connect_api_router.post("/api/v1/owner_data", status_code=HTTPStatus.CREATED)
async def api_create_owner_data(
    data: CreateOwnerData,
    user: User = Depends(check_user_exists),
) -> OwnerData:
    owner_data = await create_owner_data(user.id, data)
    return owner_data


@lnbits_cloud_connect_api_router.put("/api/v1/owner_data/{owner_data_id}", status_code=HTTPStatus.CREATED)
async def api_update_owner_data(
    owner_data_id: str,
    data: CreateOwnerData,
    user: User = Depends(check_user_exists),
) -> OwnerData:
    owner_data = await get_owner_data(user.id, owner_data_id)
    if not owner_data:
        raise HTTPException(HTTPStatus.NOT_FOUND, "Owner Data not found.")
    if owner_data.user_id != user.id:
        raise HTTPException(HTTPStatus.FORBIDDEN, "You do not own this owner data.")
    owner_data = await update_owner_data(OwnerData(**{**owner_data.dict(), **data.dict()}))
    return owner_data


@lnbits_cloud_connect_api_router.get(
    "/api/v1/owner_data/paginated",
    name="Owner Data List",
    summary="get paginated list of owner_data",
    response_description="list of owner_data",
    openapi_extra=generate_filter_params_openapi(OwnerDataFilters),
    response_model=Page[OwnerData],
)
async def api_get_owner_data_paginated(
    user: User = Depends(check_user_exists),
    filters: Filters = Depends(owner_data_filters),
) -> Page[OwnerData]:

    return await get_owner_data_paginated(
        user_id=user.id,
        filters=filters,
    )


@lnbits_cloud_connect_api_router.get(
    "/api/v1/owner_data/{owner_data_id}",
    name="Get OwnerData",
    summary="Get the owner_data with this id.",
    response_description="An owner_data or 404 if not found",
    response_model=OwnerData,
)
async def api_get_owner_data(
    owner_data_id: str,
    user: User = Depends(check_user_exists),
) -> OwnerData:

    owner_data = await get_owner_data(user.id, owner_data_id)
    if not owner_data:
        raise HTTPException(HTTPStatus.NOT_FOUND, "OwnerData not found.")

    return owner_data


@lnbits_cloud_connect_api_router.delete(
    "/api/v1/owner_data/{owner_data_id}",
    name="Delete Owner Data",
    summary="Delete the owner_data " "and optionally all its associated client_data.",
    response_description="The status of the deletion.",
    response_model=SimpleStatus,
)
async def api_delete_owner_data(
    owner_data_id: str,
    clear_client_data: bool | None = False,
    user: User = Depends(check_user_exists),
) -> SimpleStatus:

    await delete_owner_data(user.id, owner_data_id)
    if clear_client_data is True:
        # await delete all client data associated with this owner data
        pass
    return SimpleStatus(success=True, message="Owner Data Deleted")


############################# Client Data #############################
@lnbits_cloud_connect_api_router.post(
    "/api/v1/client_data/{owner_data_id}",
    name="Create Client Data",
    summary="Create new client data for the specified owner data.",
    response_description="The created client data.",
    response_model=ClientData,
    status_code=HTTPStatus.CREATED,
)
async def api_create_client_data(
    owner_data_id: str,
    data: CreateClientData,
    user: User = Depends(check_user_exists),
) -> ClientData:
    owner_data = await get_owner_data(user.id, owner_data_id)
    if not owner_data:
        raise HTTPException(HTTPStatus.NOT_FOUND, "Owner Data not found.")

    client_data = await create_client_data(owner_data_id, data)
    return client_data




@lnbits_cloud_connect_api_router.put(
    "/api/v1/client_data/{client_data_id}",
    name="Update Client Data",
    summary="Update the client_data with this id.",
    response_description="The updated client data.",
    response_model=ClientData,
)
async def api_update_client_data(
    client_data_id: str,
    data: CreateClientData,
    user: User = Depends(check_user_exists),
) -> ClientData:
    client_data = await get_client_data_by_id(client_data_id)
    if not client_data:
        raise HTTPException(HTTPStatus.NOT_FOUND, "Client Data not found.")

    owner_data = await get_owner_data(user.id, client_data.owner_data_id)
    if not owner_data:
        raise HTTPException(HTTPStatus.NOT_FOUND, "Owner Data not found.")

    client_data = await update_client_data(ClientData(**{**client_data.dict(), **data.dict()}))
    return client_data


@lnbits_cloud_connect_api_router.get(
    "/api/v1/client_data/paginated",
    name="Client Data List",
    summary="get paginated list of client_data",
    response_description="list of client_data",
    openapi_extra=generate_filter_params_openapi(ClientDataFilters),
    response_model=Page[ClientData],
)
async def api_get_client_data_paginated(
    user: User = Depends(check_user_exists),
    owner_data_id: str | None = None,
    filters: Filters = Depends(client_data_filters),
) -> Page[ClientData]:

    owner_data_ids = await get_owner_data_ids_by_user(user.id)

    if owner_data_id:
        if owner_data_id not in owner_data_ids:
            raise HTTPException(HTTPStatus.FORBIDDEN, "Not your owner data.")
        owner_data_ids = [owner_data_id]

    return await get_client_data_paginated(
        owner_data_ids=owner_data_ids,
        filters=filters,
    )


@lnbits_cloud_connect_api_router.get(
    "/api/v1/client_data/{client_data_id}",
    name="Get Client Data",
    summary="Get the client data with this id.",
    response_description="An client data or 404 if not found",
    response_model=ClientData,
)
async def api_get_client_data(
    client_data_id: str,
    user: User = Depends(check_user_exists),
) -> ClientData:

    client_data = await get_client_data_by_id(client_data_id)
    if not client_data:
        raise HTTPException(HTTPStatus.NOT_FOUND, "ClientData not found.")
    owner_data = await get_owner_data(user.id, client_data.owner_data_id)
    if not owner_data:
        raise HTTPException(HTTPStatus.NOT_FOUND, "Owner Data deleted for this Client Data.")

    return client_data


@lnbits_cloud_connect_api_router.delete(
    "/api/v1/client_data/{client_data_id}",
    name="Delete Client Data",
    summary="Delete the client_data",
    response_description="The status of the deletion.",
    response_model=SimpleStatus,
)
async def api_delete_client_data(
    client_data_id: str,
    user: User = Depends(check_user_exists),
) -> SimpleStatus:

    client_data = await get_client_data_by_id(client_data_id)
    if not client_data:
        raise HTTPException(HTTPStatus.NOT_FOUND, "ClientData not found.")
    owner_data = await get_owner_data(user.id, client_data.owner_data_id)
    if not owner_data:
        raise HTTPException(HTTPStatus.NOT_FOUND, "Owner Data deleted for this Client Data.")

    await delete_client_data(owner_data.id, client_data_id)
    return SimpleStatus(success=True, message="Client Data Deleted")


############################ Settings #############################
@lnbits_cloud_connect_api_router.get(
    "/api/v1/settings",
    name="Get Settings",
    summary="Get the settings for the current user.",
    response_description="The settings or 404 if not found",
    response_model=ExtensionSettings,
)
async def api_get_settings(
    user: User = Depends(check_user_exists),
) -> ExtensionSettings:
    user_id = "admin" if ExtensionSettings.is_admin_only() else user.id
    return await get_settings(user_id)


@lnbits_cloud_connect_api_router.put(
    "/api/v1/settings",
    name="Update Settings",
    summary="Update the settings for the current user.",
    response_description="The updated settings.",
    response_model=ExtensionSettings,
)
async def api_update_extension_settings(
    data: ExtensionSettings,
    user: User = Depends(check_user_exists),
) -> ExtensionSettings:
    if ExtensionSettings.is_admin_only() and not user.admin:
        raise HTTPException(
            HTTPStatus.FORBIDDEN,
            "Only admins can update settings.",
        )
    user_id = "admin" if ExtensionSettings.is_admin_only() else user.id
    return await update_settings(user_id, data)


############################# SSH Tunnels #############################
@lnbits_cloud_connect_api_router.post("/api/v1/ssh-tunnels", status_code=HTTPStatus.CREATED)
async def api_create_ssh_tunnel(
    data: CreateSSHTunnel,
    user: User = Depends(check_user_exists),
) -> SSHTunnel:
    from .helpers import generate_ssh_keypair, encrypt_private_key
    
    private_key, public_key = generate_ssh_keypair()
    encrypted_private_key = encrypt_private_key(private_key)
    
    tunnel = await create_ssh_tunnel(user.wallets[0].id, data, encrypted_private_key, public_key)
    return tunnel


@lnbits_cloud_connect_api_router.get(
    "/api/v1/ssh-tunnels",
    name="SSH Tunnels List",
    summary="Get paginated list of SSH tunnels",
    response_description="List of SSH tunnels",
    openapi_extra=generate_filter_params_openapi(SSHTunnelFilters),
    response_model=Page[SSHTunnel],
)
async def api_get_ssh_tunnels(
    user: User = Depends(check_user_exists),
    filters: Filters = Depends(ssh_tunnel_filters),
) -> Page[SSHTunnel]:
    try:
        return await get_ssh_tunnels_paginated(
            wallet_id=user.wallets[0].id,
            filters=filters,
        )
    except Exception as e:
        # Handle case where ssh_tunnels table doesn't exist yet
        if "no such table" in str(e).lower() or "table" in str(e).lower():
            # Return empty page if table doesn't exist yet
            from lnbits.db import Page
            return Page(data=[], total=0)
        raise HTTPException(HTTPStatus.INTERNAL_SERVER_ERROR, f"Database error: {str(e)}")


@lnbits_cloud_connect_api_router.get("/api/v1/ssh-tunnels/{tunnel_id}")
async def api_get_ssh_tunnel(
    tunnel_id: str,
    user: User = Depends(check_user_exists),
) -> SSHTunnel:
    tunnel = await get_ssh_tunnel(tunnel_id, user.wallets[0].id)
    if not tunnel:
        raise HTTPException(HTTPStatus.NOT_FOUND, "SSH tunnel not found.")
    return tunnel


@lnbits_cloud_connect_api_router.post("/api/v1/ssh-tunnels/{tunnel_id}/connect")
async def api_connect_ssh_tunnel(
    tunnel_id: str,
    user: User = Depends(check_user_exists),
) -> SimpleStatus:
    from .ssh_service import tunnel_manager
    
    tunnel = await get_ssh_tunnel(tunnel_id, user.wallets[0].id)
    if not tunnel:
        raise HTTPException(HTTPStatus.NOT_FOUND, "SSH tunnel not found.")
    
    try:
        success = await tunnel_manager.start_tunnel(tunnel)
        if not success:
            raise HTTPException(HTTPStatus.INTERNAL_SERVER_ERROR, 
                              "Failed to start SSH tunnel. Check logs for details.")
        
        return SimpleStatus(success=True, message="SSH tunnel connected.")
    except RuntimeError as e:
        raise HTTPException(HTTPStatus.BAD_REQUEST, str(e))
    except Exception as e:
        raise HTTPException(HTTPStatus.INTERNAL_SERVER_ERROR, f"Unexpected error: {str(e)}")


@lnbits_cloud_connect_api_router.post("/api/v1/ssh-tunnels/{tunnel_id}/disconnect")
async def api_disconnect_ssh_tunnel(
    tunnel_id: str,
    user: User = Depends(check_user_exists),
) -> SimpleStatus:
    from .ssh_service import tunnel_manager
    
    tunnel = await get_ssh_tunnel(tunnel_id, user.wallets[0].id)
    if not tunnel:
        raise HTTPException(HTTPStatus.NOT_FOUND, "SSH tunnel not found.")
    
    success = await tunnel_manager.stop_tunnel(tunnel_id, manual_disconnect=True)
    if not success:
        raise HTTPException(HTTPStatus.INTERNAL_SERVER_ERROR, "Failed to stop SSH tunnel.")
    
    return SimpleStatus(success=True, message="SSH tunnel disconnected.")


@lnbits_cloud_connect_api_router.get("/api/v1/ssh-tunnels/{tunnel_id}/status")
async def api_get_ssh_tunnel_status(
    tunnel_id: str,
    user: User = Depends(check_user_exists),
) -> dict:
    from .ssh_service import tunnel_manager
    
    tunnel = await get_ssh_tunnel(tunnel_id, user.wallets[0].id)
    if not tunnel:
        raise HTTPException(HTTPStatus.NOT_FOUND, "SSH tunnel not found.")
    
    status = await tunnel_manager.get_tunnel_status(tunnel_id)
    return status


@lnbits_cloud_connect_api_router.put("/api/v1/ssh-tunnels/{tunnel_id}")
async def api_update_ssh_tunnel(
    tunnel_id: str,
    data: CreateSSHTunnel,
    user: User = Depends(check_user_exists),
) -> SSHTunnel:
    tunnel = await get_ssh_tunnel(tunnel_id, user.wallets[0].id)
    if not tunnel:
        raise HTTPException(HTTPStatus.NOT_FOUND, "SSH tunnel not found.")
    
    updated_tunnel = SSHTunnel(**{**tunnel.dict(), **data.dict()})
    tunnel = await update_ssh_tunnel(updated_tunnel)
    return tunnel


@lnbits_cloud_connect_api_router.delete("/api/v1/ssh-tunnels/{tunnel_id}")
async def api_delete_ssh_tunnel(
    tunnel_id: str,
    user: User = Depends(check_user_exists),
) -> SimpleStatus:
    from .ssh_service import tunnel_manager
    
    tunnel = await get_ssh_tunnel(tunnel_id, user.wallets[0].id)
    if not tunnel:
        raise HTTPException(HTTPStatus.NOT_FOUND, "SSH tunnel not found.")
    
    await tunnel_manager.stop_tunnel(tunnel_id, manual_disconnect=True)
    await delete_ssh_tunnel(tunnel_id, user.wallets[0].id)
    
    return SimpleStatus(success=True, message="SSH tunnel deleted.")


