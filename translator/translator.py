import asyncio
from translate import Translator as tr
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import aiohttp

class EmailCollection:
    def __init__(self) -> None:
        self.index = 0
        self.emails = [
            'asylkhangr@gmail.com',
            'yerassyl.danay.nu@gmail.com',
            'yerassyl.danay.abc@gmail.com',
            'askatnis@gmail.com',
        ]

    def get(self) -> str:
        email = self.emails[self.index]
        self.index = (self.index + 1) % len(self.emails)
        return email

email = EmailCollection()

class TranslatorBot:
    def __init__(self, from_lang, to_lang:str):
        self.to_lang = to_lang
        self.from_lang = from_lang
        self.chunk_size = 499

    async def translate(self, text):
        async with aiohttp.ClientSession() as session:
            params = {
                'q': text,
                'langpair': f"{self.from_lang}|{self.to_lang}",
                'de':email.get()
            }

            async with session.get('https://api.mymemory.translated.net/get', params=params) as resp:
                result = await resp.json()
                return result.get('responseData', dict()).get('translatedText', '')

    def split_text(self, text: str, max_chunk_size: int = 499):
        sentences = re.split(r'(?<=[^A-Z].[.?]) +(?=[A-Z])', text)
        chunks = []
        current_chunk = ""
        current_count = 0
        for sentence in sentences:
            if '\n' in sentence:
                sentences_split_by_newline = sentence.split('\n')
                for new_sentence in sentences_split_by_newline:
                    if current_count + len(new_sentence) <= max_chunk_size:
                        current_chunk += new_sentence
                        current_count += len(new_sentence)
                    else:
                        chunks.append(current_chunk)
                        current_chunk = new_sentence
                        current_count = len(new_sentence)
            else:
                if current_count + len(sentence) <= max_chunk_size:
                    current_chunk += sentence
                    current_count += len(sentence)
                else:
                    chunks.append(current_chunk)
                    current_chunk = sentence
                    current_count = len(sentence)
        chunks.append(current_chunk)
        return chunks

    async def wrapper(self, text: str) -> str:
        chunks = self.split_text(text)
        tasks = [asyncio.create_task(self.translate(chunk)) for chunk in chunks]
        result = await asyncio.gather(*tasks)
        return ''.join(result)

# async def run():
#     translator = TranslatorBot('en','kk')
#     english_text = "The meaning of life is a complex and highly debated topic that has been explored by philosophers, religious figures, and scientists throughout history. Some believe that the meaning of life is to seek happiness, others believe it is to fulfill a specific purpose or destiny, and still others believe that life has no inherent meaning and that it is up to each individual to create their own purpose. Ultimately, the meaning of life may be different for each person and can change throughout one's lifetime. Some might find meaning in helping others, others in achieving personal goals, some in finding inner peace, and others in pursuing spiritual enlightenment. The meaning of life is something that is constantly being explored and redefined by each individual as they navigate their own journey through life."
#     tasks = [asyncio.create_task(translator.wrapper(english_text))]
#     result = await asyncio.gather(*tasks)
#     # print(result)
#     print(len(result))

# loop = asyncio.new_event_loop()
# asyncio.set_event_loop(loop)
# loop.run_until_complete(run())
# loop.close()

# asyncio.run(run())