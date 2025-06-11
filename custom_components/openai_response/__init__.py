import logging
import openai
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)
DOMAIN = "openai_response"

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:

    async def handle_ask_service(call: ServiceCall):
        prompt = call.data.get("prompt")
        model = call.data.get("model", "gpt-3.5-turbo")

        if not prompt:
            _LOGGER.warning("No prompt provided to OpenAI.")
            return

        try:
            response = await hass.async_add_executor_job(
                lambda: openai.ChatCompletion.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=500
                )
            )

            reply = response.choices[0].message["content"].strip()

            _LOGGER.info("OpenAI Response: %s", reply)

            # Cập nhật sensor hassio_openai_response nếu tồn tại
            entity_id = "sensor.hassio_openai_response"
            current = hass.states.get(entity_id)
            if current:
                hass.states.async_set(entity_id, "response_received", {
                    "response_text": reply,
                    "prompt": prompt,
                    "model": model
                })
            else:
                _LOGGER.warning("Sensor '%s' not found!", entity_id)

            # Hiện thông báo
            hass.components.persistent_notification.create(
                f"**Prompt:** {prompt}\n\n**Reply:** {reply}",
                title="OpenAI Response"
            )

        except Exception as e:
            _LOGGER.error("Error communicating with OpenAI: %s", e)

    hass.services.async_register(DOMAIN, "ask", handle_ask_service)
    return True
