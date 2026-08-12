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

