import json
from typing import List

from tuples import Settings, HostData


class Serializer:
    def __init__(self, servers_path: str = None, settings_path: str = None):
        self.servers_path = servers_path
        self.settings_path = settings_path

    def load_settings(self, path: str = None) -> Settings:
        raise NotImplementedError
    
    def save_settings(self, settings: Settings, path: str = None) -> None:
        raise NotImplementedError
    
    def load_servers(self, path: str = None) -> List[HostData]:
        if not path:
            path = self.servers_path
        servers = []
        try:
            with open(path, 'r') as f:
                servers_raw = json.load(f)
                for s in servers_raw:
                    servers.append(HostData(*s))
        finally:
            return servers

    def save_servers(self, servers: List[HostData], path: str = None):
        if not path:
            path = self.servers_path
        try:
            with open(path, 'w') as f:
                json.dump(servers, f)
        except Exception as e:
            raise e
            return False
        else:
            return True