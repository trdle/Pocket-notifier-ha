"""Config flow for the PocketNotifier integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_API_KEY, CONF_NAME

from .const import DEFAULT_NAME, DOMAIN

USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
        vol.Required(CONF_API_KEY): str,
    }
)


class PocketNotifierConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for PocketNotifier.

    No API key validation is performed: any key is accepted. A separate config
    entry (and therefore a separate ``notify.<name>`` service) is created per
    channel.
    """

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # The notify service name is derived from the channel name, so it
            # must be unique across config entries.
            self._async_abort_entries_match({CONF_NAME: user_input[CONF_NAME]})

            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data=user_input,
            )

        return self.async_show_form(
            step_id="user",
            data_schema=USER_SCHEMA,
            errors=errors,
        )
