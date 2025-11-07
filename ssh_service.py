import asyncio
import signal
import os
from typing import Dict, Optional
from loguru import logger

from .models import SSHTunnel
from .crud import get_ssh_tunnel_by_id, update_ssh_tunnel_connection_status
from .helpers import save_private_key_to_temp_file, cleanup_temp_key_file, decrypt_private_key


class SSHTunnelManager:
    def __init__(self):
        self.active_tunnels: Dict[str, asyncio.subprocess.Process] = {}
        self.key_files: Dict[str, str] = {}
        
    async def start_tunnel(self, tunnel: SSHTunnel) -> bool:
        """
        Start SSH tunnel for the given configuration.
        Returns True if successful, False otherwise.
        """
        if tunnel.id in self.active_tunnels:
            logger.warning(f"Tunnel {tunnel.id} is already active")
            return False
            
        try:
            private_key = decrypt_private_key(tunnel.private_key)
            public_key = tunnel.public_key
            key_file_path = save_private_key_to_temp_file(private_key)
            self.key_files[tunnel.id] = key_file_path
            
            ssh_command = [
                "ssh",
                "-N",
                "-v",  # Add verbose output for debugging
                "-o", "StrictHostKeyChecking=no",
                "-o", "UserKnownHostsFile=/dev/null",
                "-o", "ServerAliveInterval=30",
                "-o", "ServerAliveCountMax=3",
                "-o", "ConnectTimeout=10",
                "-i", key_file_path,
                "-R", f"127.0.0.1:{tunnel.remote_port}:localhost:{tunnel.local_port}",
                f"{tunnel.remote_server_user}@{tunnel.remote_server_url}"
            ]
            
            logger.info(f"Starting SSH tunnel: {' '.join(ssh_command[:-1])} {tunnel.remote_server_user}@{tunnel.remote_server_url}")
            logger.info(f"Using public key: {public_key}")
            
            process = await asyncio.create_subprocess_exec(
                *ssh_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait a moment to check for immediate errors
            await asyncio.sleep(2)
            
            if process.returncode is not None:
                # Process already exited, read error output
                stderr_output = await process.stderr.read()
                stdout_output = await process.stdout.read()
                error_msg = stderr_output.decode() + stdout_output.decode()
                logger.error(f"SSH tunnel failed to start: {error_msg}")
                raise RuntimeError(f"SSH connection failed: {error_msg}")
            
            self.active_tunnels[tunnel.id] = process
            
            await update_ssh_tunnel_connection_status(tunnel.id, True, process.pid)
            
            logger.info(f"SSH tunnel {tunnel.id} started with PID {process.pid}")
            
            asyncio.create_task(self._monitor_tunnel(tunnel.id))
            
            return True
            
        except FileNotFoundError:
            logger.error(f"SSH command not found. Please ensure SSH client is installed.")
            await self._cleanup_tunnel_resources(tunnel.id)
            return False
        except PermissionError as e:
            logger.error(f"Permission denied when creating key file for tunnel {tunnel.id}: {e}")
            await self._cleanup_tunnel_resources(tunnel.id)
            return False
        except Exception as e:
            logger.error(f"Failed to start SSH tunnel {tunnel.id}: {e}")
            await self._cleanup_tunnel_resources(tunnel.id)
            return False
    
    async def stop_tunnel(self, tunnel_id: str, manual_disconnect: bool = True) -> bool:
        """
        Stop SSH tunnel.
        Args:
            tunnel_id: ID of the tunnel to stop
            manual_disconnect: If True, prevents auto-reconnection
        Returns True if successful, False otherwise.
        """
        if tunnel_id not in self.active_tunnels:
            logger.warning(f"Tunnel {tunnel_id} is not active")
            return False
            
        try:
            process = self.active_tunnels[tunnel_id]
            
            if manual_disconnect:
                tunnel = await get_ssh_tunnel_by_id(tunnel_id)
                if tunnel:
                    tunnel.auto_reconnect = False
                    from .crud import update_ssh_tunnel
                    await update_ssh_tunnel(tunnel)
            
            process.terminate()
            
            try:
                await asyncio.wait_for(process.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                logger.warning(f"Tunnel {tunnel_id} did not terminate gracefully, killing...")
                process.kill()
                await process.wait()
            
            await self._cleanup_tunnel_resources(tunnel_id)
            
            logger.info(f"SSH tunnel {tunnel_id} stopped")
            return True
            
        except ProcessLookupError:
            logger.warning(f"Process for tunnel {tunnel_id} was already terminated")
            await self._cleanup_tunnel_resources(tunnel_id)
            return True
        except Exception as e:
            logger.error(f"Failed to stop SSH tunnel {tunnel_id}: {e}")
            await self._cleanup_tunnel_resources(tunnel_id)
            return False
    
    async def restart_tunnel(self, tunnel_id: str) -> bool:
        """
        Restart an SSH tunnel.
        """
        tunnel = await get_ssh_tunnel_by_id(tunnel_id)
        if not tunnel:
            logger.error(f"Tunnel {tunnel_id} not found")
            return False
            
        await self.stop_tunnel(tunnel_id, manual_disconnect=False)
        await asyncio.sleep(1)
        return await self.start_tunnel(tunnel)
    
    async def get_tunnel_status(self, tunnel_id: str) -> dict:
        """
        Get status information for a tunnel.
        """
        is_active = tunnel_id in self.active_tunnels
        process_id = None
        
        if is_active:
            process = self.active_tunnels[tunnel_id]
            process_id = process.pid
            
        return {
            "tunnel_id": tunnel_id,
            "is_active": is_active,
            "process_id": process_id
        }
    
    async def _monitor_tunnel(self, tunnel_id: str):
        """
        Monitor tunnel process and handle disconnections.
        """
        try:
            process = self.active_tunnels.get(tunnel_id)
            if not process:
                return
                
            await process.wait()
            
            logger.warning(f"SSH tunnel {tunnel_id} process ended")
            
            tunnel = await get_ssh_tunnel_by_id(tunnel_id)
            if not tunnel:
                await self._cleanup_tunnel_resources(tunnel_id)
                return
                
            await update_ssh_tunnel_connection_status(tunnel_id, False, None)
            
            if tunnel.auto_reconnect:
                logger.info(f"Auto-reconnecting tunnel {tunnel_id}")
                await asyncio.sleep(5)
                await self.restart_tunnel(tunnel_id)
            else:
                await self._cleanup_tunnel_resources(tunnel_id)
                
        except Exception as e:
            logger.error(f"Error monitoring tunnel {tunnel_id}: {e}")
            await self._cleanup_tunnel_resources(tunnel_id)
    
    async def _cleanup_tunnel_resources(self, tunnel_id: str):
        """
        Clean up resources for a tunnel.
        """
        if tunnel_id in self.active_tunnels:
            del self.active_tunnels[tunnel_id]
            
        if tunnel_id in self.key_files:
            cleanup_temp_key_file(self.key_files[tunnel_id])
            del self.key_files[tunnel_id]
            
        await update_ssh_tunnel_connection_status(tunnel_id, False, None)
    
    async def stop_all_tunnels(self):
        """
        Stop all active tunnels.
        """
        tunnel_ids = list(self.active_tunnels.keys())
        for tunnel_id in tunnel_ids:
            await self.stop_tunnel(tunnel_id, manual_disconnect=True)
    
    async def get_all_active_tunnels(self) -> list[str]:
        """
        Get list of all active tunnel IDs.
        """
        return list(self.active_tunnels.keys())


tunnel_manager = SSHTunnelManager()