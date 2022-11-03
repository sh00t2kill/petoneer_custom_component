from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult


from .const import CONF_SERIAL, DOMAIN


class RevogiFlowHandler(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Solcast Solar."""

    VERSION = 2

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> RevogirOptionFlowHandler:
        """Get the options flow for this handler."""
        return RevogiOptionFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle a flow initiated by the user."""
        if user_input is not None:
            return self.async_create_entry(
                title= "Petoneer Revogi",
                data = {},
                options={
                    CONF_USERNAME: user_input[CONF_USERNAME],
                    CONF_PASSWORD: user_input[CONF_PASSWORD],
                    CONF_SERIAL: user_input[CONF_SERIAL],
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_USERNAME, default="Username"): str,
                    vol.Required(CONF_PASSWORD, default="Password"): str,
                    vol.Required(CONF_SERIAL, default="Fountain Serial"): str,
                }
            ),
        )


class RevogiOptionFlowHandler(OptionsFlow):
    """Handle options."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="Petoneer Revogi", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_USERNAME,
                        default=self.config_entry.options.get(CONF_USERNAME),
                    ): str,
                    vol.Required(
                        CONF_PASSWORD,
                        default=self.config_entry.options.get(CONF_PASSWORD),
                    ): str,
                    vol.Required(
                        CONF_SERIAL,
                        default=self.config_entry.options.get(CONF_SERIAL),
                    ): str,
                }
            ),
        )
