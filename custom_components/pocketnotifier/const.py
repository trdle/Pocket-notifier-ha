"""Constants for the PocketNotifier integration."""

from typing import Final

DOMAIN: Final = "pocketnotifier"

# Key under which the original HA config is stored, so the notify platform
# can be loaded via discovery (mirrors the upstream Pushover pattern).
DATA_HASS_CONFIG: Final = "pocketnotifier_hass_config"

DEFAULT_NAME: Final = "PocketNotifier"

# PocketNotifier relay endpoint that fans a notification out to the phones
# subscribed to the channel identified by the API key.
API_URL: Final = "https://pocketnotifier.vanmo.se/api/notify"

# Header used to authenticate the channel.
ATTR_API_KEY_HEADER: Final = "X-Api-Key"

# Optional fields that can be passed through the notify service `data` dict.
ATTR_URL: Final = "url"
ATTR_PRIORITY: Final = "priority"

# Allowed values for the optional `priority` field. The relay defaults to
# "normal" when omitted.
PRIORITIES: Final = ("quiet", "normal", "urgent")
