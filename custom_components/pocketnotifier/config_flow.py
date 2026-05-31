"""Config flow for the PocketNotifier integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_API_KEY, CONF_NAME
from homeassistant.util import slugify

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
            name = user_input[CONF_NAME].strip()
            slug = slugify(name)

            if not slug:
                # An empty name, or one made only of characters that slugify
                # away (e.g. punctuation/emoji), cannot form a valid
                # notify.<name> service.
                errors[CONF_NAME] = "invalid_name"
            elif any(
                slugify(entry.data[CONF_NAME]) == slug
                for entry in self._async_current_entries()
            ):
                # The notify service name is derived from the channel name via
                # slugify, so two names that slugify to the same id would
                # collide on a single notify.<slug> service.
                return self.async_abort(reason="already_configured")
            else:
                user_input[CONF_NAME] = name
                return self.async_create_entry(title=name, data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=USER_SCHEMA,
            errors=errors,
        )
