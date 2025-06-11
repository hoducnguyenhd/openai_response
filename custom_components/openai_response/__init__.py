import logging
import openai
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)
DOMAIN = "openai_response"

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:

    async def handle_ask_service(call: ServiceCall):
        prompt = call.data.get("prompt")
        model = call.data.get("model", "text-davinci-003")

        if not prompt:
            _LOGGER.warning("No prompt provided to OpenAI.")
            return

        try:
            response = await hass.async_add_executor_job(
                lambda: openai.Completion.create(
                    model=model,
                    prompt=prompt,
                    temperature=0.7,
                    max_tokens=300,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0
                )
            )
            reply = response.choices[0].text.strip()

            _LOGGER.info("OpenAI Response: %s", reply)

            # Gửi kết quả về sensor hassio_openai_response nếu có
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

            # Gửi notification (nếu cần)
            hass.components.persistent_notification.create(
                f"**Prompt:** {prompt}\n\n**Reply:** {reply}",
                title="OpenAI Response"
            )

        except Exception as e:
            _LOGGER.error("Error communicating with OpenAI: %s", e)

    hass.services.async_register(DOMAIN, "ask", handle_ask_service)
    return True
