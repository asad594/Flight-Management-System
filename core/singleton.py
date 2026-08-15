"""
Singleton Pattern Module for SkyBound Flight Management System.

Ensures a single shared instance of the AppConfigManager exists across
the application lifecycle for managing global runtime configuration settings.
"""

from typing import Any, Optional


class AppConfigManager:
    """
    Singleton class managing global application configurations and system settings.

    Implements the GoF Singleton Design Pattern using __new__ override to guarantee
    that only one configuration manager instance exists throughout runtime.
    """
    _instance: Optional["AppConfigManager"] = None

    def __new__(cls) -> "AppConfigManager":
        """Constructs or returns the existing singleton AppConfigManager instance."""
        if cls._instance is None:
            cls._instance = super(AppConfigManager, cls).__new__(cls)
            # Initialize default system settings
            cls._instance.currency = "USD"
            cls._instance.system_name = "SkyBound"
            cls._instance.tax_rate = 0.05
        return cls._instance

    def get_setting(self, key: str, default: Optional[Any] = None) -> Optional[Any]:
        """
        Retrieves a global configuration setting by key name.

        Args:
            key: The attribute name of the configuration setting.
            default: Optional fallback value if the key does not exist.

        Returns:
            The setting value, or default if the key is not defined.
        """
        return getattr(self, key, default)

    def set_setting(self, key: str, value: Any) -> None:
        """
        Sets or updates a global configuration setting dynamically.

        Args:
            key: The attribute name of the configuration setting to update or create.
            value: The value to assign to the configuration key.
        """
        setattr(self, key, value)

    def has_setting(self, key: str) -> bool:
        """
        Checks whether a configuration key is defined on the singleton instance.

        Args:
            key: The attribute name to check.

        Returns:
            True if the attribute exists on the instance, False otherwise.
        """
        return hasattr(self, key)



