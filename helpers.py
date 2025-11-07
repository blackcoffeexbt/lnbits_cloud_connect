# Description: A place for helper functions.

import re
import tempfile
import os
from typing import Tuple
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from lnbits.settings import settings
from loguru import logger


def is_valid_email_address(email: str) -> bool:
    email_regex = r"[A-Za-z0-9\._%+-]+@[A-Za-z0-9\.-]+\.[A-Za-z]{2,63}"
    return re.fullmatch(email_regex, email) is not None


def generate_ssh_keypair() -> Tuple[str, str]:
    """
    Generate SSH RSA keypair.
    Returns tuple of (private_key_pem, public_key_openssh)
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    public_key = private_key.public_key()
    public_openssh = public_key.public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH
    )
    # log the public key for user convenience
    logger.info(f"Generated SSH keypair for user: {public_openssh.decode('utf-8')}")
    
    return private_pem.decode('utf-8'), public_openssh.decode('utf-8')


def encrypt_private_key(private_key: str) -> str:
    """
    Encrypt private key using LNBits encryption settings.
    For now, return as-is. In production, implement proper encryption.
    """
    return private_key


def decrypt_private_key(encrypted_private_key: str) -> str:
    """
    Decrypt private key using LNBits encryption settings.
    For now, return as-is. In production, implement proper decryption.
    """
    return encrypted_private_key


def save_private_key_to_temp_file(private_key: str) -> str:
    """
    Save private key to temporary file for SSH usage.
    Returns the file path.
    """
    fd, temp_path = tempfile.mkstemp(suffix='.key')
    # log the temp file path for debugging
    logger.debug(f"Saving private key to temporary file: {temp_path}")
    try:
        with os.fdopen(fd, 'w') as f:
            f.write(private_key)
        os.chmod(temp_path, 0o600)
        return temp_path
    except PermissionError as e:
        os.close(fd)
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise PermissionError(f"Unable to set proper permissions on SSH key file: {e}")
    except Exception as e:
        os.close(fd)
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise RuntimeError(f"Failed to create temporary SSH key file: {e}")


def cleanup_temp_key_file(key_file_path: str) -> None:
    """
    Securely remove temporary key file.
    """
    try:
        if os.path.exists(key_file_path):
            os.unlink(key_file_path)
    except Exception:
        pass
