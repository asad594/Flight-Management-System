from typing import Any, Optional

class AppConfigManager:
    """Singleton pattern implementation managing global application configurations."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppConfigManager, cls).__new__(cls)
            # Initialize default settings
            cls._instance.currency = "USD"
            cls._instance.system_name = "SkyBound"
            cls._instance.tax_rate = 0.05
        return cls._instance

    def get_setting(self, key: str) -> Optional[Any]:
        """Retrieves a global configuration setting by key."""
        return getattr(self, key, None)

    def set_setting(self, key: str, value: Any) -> None:
        """Sets or updates a global configuration setting dynamically."""
        setattr(self, key, value)

    def has_setting(self, key: str) -> bool:
        """Checks whether a configuration key is defined."""
        return hasattr(self, key)


