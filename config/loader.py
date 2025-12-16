import yaml
import os
from .models import BaseConfig

_current_config: BaseConfig | None = None

def load_config(config_path: str = "config/base_config.yaml") -> BaseConfig:
    global _current_config
    
    if not os.path.exists(config_path):
        # Return default if no file found, or raise error? 
        # For assignment, let's assume file must exist or we return default.
        # But better to error if explicit path given and missing.
        if config_path != "config/base_config.yaml":
             raise FileNotFoundError(f"Config file not found: {config_path}")
        # Return default minimal config
        return BaseConfig()
        
    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        
    _current_config = BaseConfig(**data)
    return _current_config

def get_config() -> BaseConfig:
    global _current_config
    if _current_config is None:
        return load_config()
    return _current_config
