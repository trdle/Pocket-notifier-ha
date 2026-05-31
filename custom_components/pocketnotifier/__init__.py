"""The PocketNotifier integration.

Each config entry represents a single PocketNotifier channel (one API key +
a human-readable name) and is exposed as a legacy ``notify.<channel_name>``
service via discovery. This mirrors the pattern used by the upstream Pushover
integration, which is deliberately chosen over the modern notify *entity*
platform because only the legacy platform supports the ``data: {url: ...}``
passthrough that PocketNotifier relies on.
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

    # `async_setup` always runs before any `async_setup_entry`, so
    # DATA_HASS_CONFIG is guaranteed to be present here.
    hass.async_create_task(
        discovery.async_load_platform(
            hass,
            Platform.NOTIFY,
            DOMAIN,
            {
                CONF_NAME: entry.data[CONF_NAME],
                "entry_id": entry.entry_id,
            },
            hass.data[DATA_HASS_CONFIG],
        )
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry.

    The legacy notify platform exposes no hook to unregister a single
    ``notify.<name>`` service; its only reset entry point
    (``notify.legacy.async_reset_platform``) is domain-wide and would tear
    down *every* channel at once, so we intentionally do not call it. We drop
    the stored API key; the already-constructed service captured its key at
    build time and never re-reads ``hass.data``, so it keeps working and will
    not error until the next restart. Re-adding a channel with the same name
    simply re-registers the service with the new key. This matches the
    upstream Pushover behaviour.
    """
    hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return True
