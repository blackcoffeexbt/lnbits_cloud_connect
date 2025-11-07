# the migration file is where you build your database tables
# If you create a new release for your extension ,
# remember the migration file is like a blockchain, never edit only add!

empty_dict: dict[str, str] = {}


async def m001_extension_settings(db):
    """
    Initial settings table.
    """

    await db.execute(
        f"""
        CREATE TABLE lnbits_cloud_connect.extension_settings (
            id TEXT NOT NULL,
            name TEXT,
            updated_at TIMESTAMP NOT NULL DEFAULT {db.timestamp_now}
        );
    """
    )




async def m002_owner_data(db):
    """
    Initial owner data table.
    """

    await db.execute(
        f"""
        CREATE TABLE lnbits_cloud_connect.owner_data (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            name TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT {db.timestamp_now},
            updated_at TIMESTAMP NOT NULL DEFAULT {db.timestamp_now}
        );
    """
    )


async def m003_client_data(db):
    """
    Initial client data table.
    """

    await db.execute(
        f"""
        CREATE TABLE lnbits_cloud_connect.client_data (
            id TEXT PRIMARY KEY,
            owner_data_id TEXT NOT NULL,
            name TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT {db.timestamp_now},
            updated_at TIMESTAMP NOT NULL DEFAULT {db.timestamp_now}
        );
    """
    )


async def m004_add_ssh_fields_to_owner_data(db):
    """
    Add SSH server configuration fields to owner_data table.
    """
    
    await db.execute(
        """
        ALTER TABLE lnbits_cloud_connect.owner_data 
        ADD COLUMN remote_server_user TEXT;
        """
    )
    
    await db.execute(
        """
        ALTER TABLE lnbits_cloud_connect.owner_data 
        ADD COLUMN remote_server_url TEXT;
        """
    )
    
    await db.execute(
        """
        ALTER TABLE lnbits_cloud_connect.owner_data 
        ADD COLUMN local_port INTEGER;
        """
    )
    
    await db.execute(
        """
        ALTER TABLE lnbits_cloud_connect.owner_data 
        ADD COLUMN remote_port INTEGER;
        """
    )


async def m005_ssh_tunnel_table(db):
    """
    Create SSH tunnel configuration table.
    """

    await db.execute(
        f"""
        CREATE TABLE lnbits_cloud_connect.ssh_tunnels (
            id TEXT PRIMARY KEY,
            wallet_id TEXT NOT NULL,
            name TEXT NOT NULL,
            remote_server_user TEXT NOT NULL,
            remote_server_url TEXT NOT NULL,
            local_port INTEGER NOT NULL,
            remote_port INTEGER NOT NULL,
            private_key TEXT NOT NULL,
            public_key TEXT NOT NULL,
            is_connected BOOLEAN NOT NULL DEFAULT 0,
            auto_reconnect BOOLEAN NOT NULL DEFAULT 1,
            process_id INTEGER,
            created_at TIMESTAMP NOT NULL DEFAULT {db.timestamp_now},
            updated_at TIMESTAMP NOT NULL DEFAULT {db.timestamp_now}
        );
    """
    )


async def m006_fix_ssh_tunnel_timestamps(db):
    """
    Fix timestamp format issues in ssh_tunnels table.
    """
    # Drop the table if it exists with wrong format and recreate it
    await db.execute(
        """
        DROP TABLE IF EXISTS lnbits_cloud_connect.ssh_tunnels;
        """
    )
    
    # Recreate with proper timestamp handling
    await db.execute(
        f"""
        CREATE TABLE lnbits_cloud_connect.ssh_tunnels (
            id TEXT PRIMARY KEY,
            wallet_id TEXT NOT NULL,
            name TEXT NOT NULL,
            remote_server_user TEXT NOT NULL,
            remote_server_url TEXT NOT NULL,
            local_port INTEGER NOT NULL,
            remote_port INTEGER NOT NULL,
            private_key TEXT NOT NULL,
            public_key TEXT NOT NULL,
            is_connected INTEGER NOT NULL DEFAULT 0,
            auto_reconnect INTEGER NOT NULL DEFAULT 1,
            process_id INTEGER,
            created_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),
            updated_at INTEGER NOT NULL DEFAULT (strftime('%s', 'now'))
        );
    """
    )


async def m007_add_startup_enabled_to_ssh_tunnels(db):
    """
    Add startup_enabled field to ssh_tunnels table.
    """
    
    await db.execute(
        """
        ALTER TABLE lnbits_cloud_connect.ssh_tunnels 
        ADD COLUMN startup_enabled INTEGER NOT NULL DEFAULT 0;
        """
    )