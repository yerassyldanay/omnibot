import json
import aiohttp
from pprint import pprint

import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class OpenAIChatGPT:
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def generate_response(self, message):
        headers = {'Authorization': 'Bearer ' + self.api_key}
        model = 'text-davinci-003'
        payload = {
            "model": model,
            "prompt": message,
            "max_tokens": 3000,
            "temperature": 0.9,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post('https://api.openai.com/v1/completions',
                                    json=payload, headers=headers) as resp:
                response = await resp.json()

        logger.info(response)

        choices = response.get('choices', [])
        if len(choices) == 0:
            # pprint(response)
            return 'ERROR'

        return choices[0].get('text', '')
