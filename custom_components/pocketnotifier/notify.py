"""PocketNotifier platform for the notify component."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp

from homeassistant.components.notify import (
    ATTR_DATA,
    ATTR_TITLE,
    ATTR_TITLE_DEFAULT,
    BaseNotificationService,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import ATTR_API_KEY_HEADER, ATTR_URL, API_URL, DOMAIN

_LOGGER = logging.getLogger(__name__)

# Be generous: the relay fans out to multiple phones.
_TIMEOUT = aiohttp.ClientTimeout(total=10)


async def async_get_service(
    hass: HomeAssistant,
    config: ConfigType,
    discovery_info: DiscoveryInfoType | None = None,
) -> PocketNotifierNotificationService | None:
    """Get the PocketNotifier notification service."""
    if discovery_info is None:
        return None

    api_key: str = hass.data[DOMAIN][discovery_info["entry_id"]]
    return PocketNotifierNotificationService(hass, api_key)


class PocketNotifierNotificationService(BaseNotificationService):
    """Implement the notification service for a PocketNotifier channel."""

    def __init__(self, hass: HomeAssistant, api_key: str) -> None:
        """Initialize the service."""
        self._hass = hass
        self._api_key = api_key

    async def async_send_message(self, message: str = "", **kwargs: Any) -> None:
        """Send a notification to the PocketNotifier channel."""
        title = kwargs.get(ATTR_TITLE, ATTR_TITLE_DEFAULT)
        data = kwargs.get(ATTR_DATA) or {}

        payload: dict[str, Any] = {"title": title, "body": message}
        # `url` is optional and only passed through when supplied via the
        # service `data` field, e.g. `data: {url: "https://..."}`.
        if (url := data.get(ATTR_URL)) is not None:
            payload[ATTR_URL] = url

        session = async_get_clientsession(self._hass)
        try:
            response = await session.post(
                API_URL,
                headers={ATTR_API_KEY_HEADER: self._api_key},
                json=payload,
                timeout=_TIMEOUT,
            )
            response.raise_for_status()
        except aiohttp.ClientResponseError as err:
            raise HomeAssistantError(
                f"PocketNotifier returned HTTP {err.status} ({err.message}). "
                "Check that the channel API key is correct."
            ) from err
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise HomeAssistantError(
                f"Error sending PocketNotifier notification: {err}"
            ) from err
