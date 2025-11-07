from datetime import datetime, timezone

from lnbits.db import FilterModel
from pydantic import BaseModel, Field


########################### Owner Data ############################
class CreateOwnerData(BaseModel):
    name: str | None
    remote_server_user: str | None = None
    remote_server_url: str | None = None
    local_port: int | None = None
    remote_port: int | None = None


class OwnerData(BaseModel):
    id: str
    user_id: str
    name: str | None
    remote_server_user: str | None = None
    remote_server_url: str | None = None  
    local_port: int | None = None
    remote_port: int | None = None
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OwnerDataFilters(FilterModel):
    __search_fields__ = [
        "name",
    ]

    __sort_fields__ = [
        "name",
        
        "created_at",
        "updated_at",
    ]

    created_at: datetime | None
    updated_at: datetime | None


################################# Client Data ###########################


class CreateClientData(BaseModel):
    name: str | None
    


class ClientData(BaseModel):
    id: str
    owner_data_id: str
    name: str | None
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))




class ClientDataFilters(FilterModel):
    __search_fields__ = [
        "name",
    ]

    __sort_fields__ = [
        "name",
        
        "created_at",
        "updated_at",
    ]

    created_at: datetime | None
    updated_at: datetime | None


############################ SSH Tunnel Models #############################
class CreateSSHTunnel(BaseModel):
    name: str
    remote_server_user: str
    remote_server_url: str
    local_port: int
    remote_port: int
    auto_reconnect: bool = True


class SSHTunnel(BaseModel):
    id: str
    wallet_id: str
    name: str
    remote_server_user: str
    remote_server_url: str
    local_port: int
    remote_port: int
    private_key: str
    public_key: str
    is_connected: bool = False
    auto_reconnect: bool = True
    process_id: int | None = None
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate_booleans
    
    @classmethod
    def validate_booleans(cls, v):
        if isinstance(v, dict):
            # Convert integer fields to booleans for SQLite compatibility
            if 'is_connected' in v and isinstance(v['is_connected'], int):
                v['is_connected'] = bool(v['is_connected'])
            if 'auto_reconnect' in v and isinstance(v['auto_reconnect'], int):
                v['auto_reconnect'] = bool(v['auto_reconnect'])
        return v


class SSHTunnelFilters(FilterModel):
    __search_fields__ = [
        "name",
        "remote_server_user", 
        "remote_server_url",
    ]

    __sort_fields__ = [
        "name",
        "remote_server_user",
        "remote_server_url", 
        "is_connected",
        "created_at",
        "updated_at",
    ]

    wallet_id: str | None = None
    is_connected: bool | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


############################ Settings #############################
class ExtensionSettings(BaseModel):
    name: str | None
    

    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def is_admin_only(cls) -> bool:
        return bool("False" == "True")


class UserExtensionSettings(ExtensionSettings):
    id: str


