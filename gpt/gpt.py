import aiohttp

class OpenAIChatGPT:
    def __init__(self, api_key):
        self.api_key = api_key

    async def generate_response(self, message):
        headers = {'Authorization': 'Bearer ' + self.api_key}
        model = 'text-davinci-002'
        prompt = (f"{message}\n\n"
                  f"Model ID: {model}\n"
                  f"Max tokens: 100\n"
                  f"Temperature: 0.5")
        payload = {
            "model": model,
            "prompt": message,
            "max_tokens": 100,
            "temperature": 0.5,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post('https://api.openai.com/v1/completions',
                                    json=payload, headers=headers) as resp:
                response = await resp.json()

        return response['choices'][0]['text']
