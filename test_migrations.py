#!/usr/bin/env python3
"""
Simple script to test and manually run migrations if needed.
Run this in the LNBits environment to check migration status.
"""

import asyncio
import sys
from crud import db

async def test_migrations():
    """Test if migrations have been applied"""
    try:
        # Try to check if ssh_tunnels table exists
        result = await db.fetchall(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='ssh_tunnels';"
        )
        
        if result:
            print("✅ ssh_tunnels table exists")
            
            # Check table structure
            columns = await db.fetchall("PRAGMA table_info(ssh_tunnels);")
            print(f"📋 Table columns: {len(columns)}")
            for col in columns:
                print(f"  - {col['name']}: {col['type']}")
                
            # Check if there's any data
            count = await db.fetchone("SELECT COUNT(*) as count FROM lnbits_cloud_connect.ssh_tunnels;")
            print(f"📊 Records in table: {count['count'] if count else 0}")
            
        else:
            print("❌ ssh_tunnels table does not exist")
            print("🔧 Migrations may need to be applied")
            
    except Exception as e:
        print(f"❌ Error checking migrations: {e}")
        print("🔧 This likely means the extension schema doesn't exist yet")

if __name__ == "__main__":
    try:
        asyncio.run(test_migrations())
    except Exception as e:
        print(f"Failed to run migration test: {e}")
        sys.exit(1)