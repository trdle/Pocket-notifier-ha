"""The PocketNotifier integration.

Each config entry represents a single PocketNotifier channel (one API key +
a human-readable name) and is exposed as a legacy ``notify.<channel_name>``
service via discovery. This mirrors the pattern used by the upstream Pushover,
ntfy, Gotify and Bark integrations.
"""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY, CONF_NAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv, discovery
from homeassistant.helpers.typing import ConfigType

from .const import DATA_HASS_CONFIG, DOMAIN

# This integration is only configurable through the UI (config entries).
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the PocketNotifier component."""
    # Stash the global HA config so the notify platform can be loaded through
    # discovery during async_setup_entry.
    hass.data[DATA_HASS_CONFIG] = config
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up PocketNotifier from a config entry.

    No API key validation is performed here by design: any key is accepted and
    delivery failures only surface (and are logged) when a notification is
    actually sent.
    """
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = entry.data[CONF_API_KEY]

    hass.async_create_task(
        discovery.async_load_platform(
            hass,
            Platform.NOTIFY,
            DOMAIN,
            {
                CONF_NAME: entry.data[CONF_NAME],
                "entry_id": entry.entry_id,
            },
            hass.data.get(DATA_HASS_CONFIG) or {},
        )
    )

    return True
