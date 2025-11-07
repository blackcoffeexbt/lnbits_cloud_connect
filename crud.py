# Description: This file contains the CRUD operations for talking to the database.


from lnbits.db import Database, Filters, Page
from lnbits.helpers import urlsafe_short_hash

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
    UserExtensionSettings,  #  
)

db = Database("ext_lnbits_cloud_connect")


########################### Owner Data ############################
async def create_owner_data(user_id: str, data: CreateOwnerData) -> OwnerData:
    owner_data = OwnerData(**data.dict(), id=urlsafe_short_hash(), user_id=user_id)
    await db.insert("lnbits_cloud_connect.owner_data", owner_data)
    return owner_data


async def get_owner_data(
    user_id: str,
    owner_data_id: str,
) -> OwnerData | None:
    return await db.fetchone(
        """
            SELECT * FROM lnbits_cloud_connect.owner_data
            WHERE id = :id AND user_id = :user_id
        """,
        {"id": owner_data_id, "user_id": user_id},
        OwnerData,
    )


async def get_owner_data_by_id(
    owner_data_id: str,
) -> OwnerData | None:
    return await db.fetchone(
        """
            SELECT * FROM lnbits_cloud_connect.owner_data
            WHERE id = :id
        """,
        {"id": owner_data_id},
        OwnerData,
    )


async def get_owner_data_ids_by_user(
    user_id: str,
) -> list[str]:
    rows: list[dict] = await db.fetchall(
        """
            SELECT DISTINCT id FROM lnbits_cloud_connect.owner_data
            WHERE user_id = :user_id
        """,
        {"user_id": user_id},
    )

    return [row["id"] for row in rows]


async def get_owner_data_paginated(
    user_id: str | None = None,
    filters: Filters[OwnerDataFilters] | None = None,
) -> Page[OwnerData]:
    where = []
    values = {}
    if user_id:
        where.append("user_id = :user_id")
        values["user_id"] = user_id

    return await db.fetch_page(
        "SELECT * FROM lnbits_cloud_connect.owner_data",
        where=where,
        values=values,
        filters=filters,
        model=OwnerData,
    )


async def update_owner_data(data: OwnerData) -> OwnerData:
    await db.update("lnbits_cloud_connect.owner_data", data)
    return data


async def delete_owner_data(user_id: str, owner_data_id: str) -> None:
    await db.execute(
        """
            DELETE FROM lnbits_cloud_connect.owner_data
            WHERE id = :id AND user_id = :user_id
        """,
        {"id": owner_data_id, "user_id": user_id},
    )


################################# Client Data ###########################


async def create_client_data(owner_data_id: str, data: CreateClientData) -> ClientData:
    client_data = ClientData(**data.dict(), id=urlsafe_short_hash(), owner_data_id=owner_data_id)
    await db.insert("lnbits_cloud_connect.client_data", client_data)
    return client_data


async def get_client_data(
    owner_data_id: str,
    client_data_id: str,
) -> ClientData | None:
    return await db.fetchone(
        """
            SELECT * FROM lnbits_cloud_connect.client_data
            WHERE id = :id AND owner_data_id = :owner_data_id
        """,
        {"id": client_data_id, "owner_data_id": owner_data_id},
        ClientData,
    )


async def get_client_data_by_id(
    client_data_id: str,
) -> ClientData | None:
    return await db.fetchone(
        """
            SELECT * FROM lnbits_cloud_connect.client_data
            WHERE id = :id
        """,
        {"id": client_data_id},
        ClientData,
    )


async def get_client_data_paginated(
    owner_data_ids: list[str] | None = None,
    filters: Filters[ClientDataFilters] | None = None,
) -> Page[ClientData]:

    if not owner_data_ids:
        return Page(data=[], total=0)

    where = []
    values = {}
    id_clause = []
    for i, item_id in enumerate(owner_data_ids):
        # owner_data_ids are not user input, but DB entries, so this is safe
        owner_data_id = f"owner_data_id__{i}"
        id_clause.append(f"owner_data_id = :{owner_data_id}")
        values[owner_data_id] = item_id
    or_clause = " OR ".join(id_clause)
    where.append(f"({or_clause})")

    return await db.fetch_page(
        "SELECT * FROM lnbits_cloud_connect.client_data",
        where=where,
        values=values,
        filters=filters,
        model=ClientData,
    )


async def update_client_data(data: ClientData) -> ClientData:
    await db.update("lnbits_cloud_connect.client_data", data)
    return data


async def delete_client_data(owner_data_id: str, client_data_id: str) -> None:
    await db.execute(
        """
            DELETE FROM lnbits_cloud_connect.client_data
            WHERE id = :id AND owner_data_id = :owner_data_id
        """,
        {"id": client_data_id, "owner_data_id": owner_data_id},
    )


############################ Settings #############################
async def create_extension_settings(user_id: str, data: ExtensionSettings) -> ExtensionSettings:
    settings = UserExtensionSettings(**data.dict(), id=user_id)
    await db.insert("lnbits_cloud_connect.extension_settings", settings)
    return settings


async def get_extension_settings(
    user_id: str,
) -> ExtensionSettings | None:
    return await db.fetchone(
        """
            SELECT * FROM lnbits_cloud_connect.extension_settings
            WHERE id = :user_id
        """,
        {"user_id": user_id},
        ExtensionSettings,
    )


async def update_extension_settings(user_id: str, data: ExtensionSettings) -> ExtensionSettings:
    settings = UserExtensionSettings(**data.dict(), id=user_id)
    await db.update("lnbits_cloud_connect.extension_settings", settings)
    return settings


############################ SSH Tunnels ############################
async def create_ssh_tunnel(wallet_id: str, data: CreateSSHTunnel, private_key: str, public_key: str) -> SSHTunnel:
    tunnel = SSHTunnel(
        **data.dict(),
        id=urlsafe_short_hash(),
        wallet_id=wallet_id,
        private_key=private_key,
        public_key=public_key
    )
    await db.insert("lnbits_cloud_connect.ssh_tunnels", tunnel)
    return tunnel


async def get_ssh_tunnel(tunnel_id: str, wallet_id: str) -> SSHTunnel | None:
    return await db.fetchone(
        """
            SELECT * FROM lnbits_cloud_connect.ssh_tunnels
            WHERE id = :id AND wallet_id = :wallet_id
        """,
        {"id": tunnel_id, "wallet_id": wallet_id},
        SSHTunnel,
    )


async def get_ssh_tunnel_by_id(tunnel_id: str) -> SSHTunnel | None:
    return await db.fetchone(
        """
            SELECT * FROM lnbits_cloud_connect.ssh_tunnels
            WHERE id = :id
        """,
        {"id": tunnel_id},
        SSHTunnel,
    )


async def get_ssh_tunnels_paginated(
    wallet_id: str | None = None,
    filters: Filters[SSHTunnelFilters] | None = None,
) -> Page[SSHTunnel]:
    where = []
    values = {}
    if wallet_id:
        where.append("wallet_id = :wallet_id")
        values["wallet_id"] = wallet_id

    return await db.fetch_page(
        "SELECT * FROM lnbits_cloud_connect.ssh_tunnels",
        where=where,
        values=values,
        filters=filters,
        model=SSHTunnel,
    )


async def get_all_ssh_tunnels() -> list[SSHTunnel]:
    return await db.fetchall(
        "SELECT * FROM lnbits_cloud_connect.ssh_tunnels",
        model=SSHTunnel,
    )


async def get_connected_ssh_tunnels() -> list[SSHTunnel]:
    return await db.fetchall(
        """
            SELECT * FROM lnbits_cloud_connect.ssh_tunnels
            WHERE is_connected = 1
        """,
        model=SSHTunnel,
    )


async def update_ssh_tunnel(data: SSHTunnel) -> SSHTunnel:
    await db.update("lnbits_cloud_connect.ssh_tunnels", data)
    return data


async def update_ssh_tunnel_connection_status(tunnel_id: str, is_connected: bool, process_id: int | None = None) -> None:
    await db.execute(
        """
            UPDATE lnbits_cloud_connect.ssh_tunnels
            SET is_connected = :is_connected, process_id = :process_id, updated_at = strftime('%s', 'now')
            WHERE id = :id
        """,
        {"id": tunnel_id, "is_connected": int(is_connected), "process_id": process_id},
    )


async def delete_ssh_tunnel(tunnel_id: str, wallet_id: str) -> None:
    await db.execute(
        """
            DELETE FROM lnbits_cloud_connect.ssh_tunnels
            WHERE id = :id AND wallet_id = :wallet_id
        """,
        {"id": tunnel_id, "wallet_id": wallet_id},
    )


