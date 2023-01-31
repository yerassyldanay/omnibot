from translate import Translator as tr
import re
from concurrent.futures import ThreadPoolExecutor, as_completed 

class TranslatorBot:
    def __init__(self, to_lang:str):
        self.to_lang = to_lang
        self.translator = tr(to_lang=self.to_lang)
        self.chunk_size = 250

    def split_text(self, text: str, max_chunk_size: int = 500):
        sentences = re.split(r'(?<=[^A-Z].[.?]) +(?=[A-Z])', text)
        chunks = []
        current_chunk = ""
        current_count = 0
        for sentence in sentences:
            if current_count + len(sentence) <= max_chunk_size:
                current_chunk += sentence
                current_count += len(sentence)
            else:
                chunks.append(current_chunk)
                current_chunk = sentence
                current_count = len(sentence)
        chunks.append(current_chunk)
        return chunks

    def translate(self, text: str) -> str:
        return self.translator.translate(text)

    def wrapper(self, text: str) -> str:
        chunks = self.split_text(text)
        with ThreadPoolExecutor() as executor:
            translated_chunks = list(executor.map(self.translate, chunks))
        return ' '.join(translated_chunks)

def run():
    translator = TranslatorBot('kk')
    english_text = "The meaning of life is a complex and highly debated topic that has been explored by philosophers, religious figures, and scientists throughout history. Some believe that the meaning of life is to seek happiness, others believe it is to fulfill a specific purpose or destiny, and still others believe that life has no inherent meaning and that it is up to each individual to create their own purpose. Ultimately, the meaning of life may be different for each person and can change throughout one's lifetime. Some might find meaning in helping others, others in achieving personal goals, some in finding inner peace, and others in pursuing spiritual enlightenment. The meaning of life is something that is constantly being explored and redefined by each individual as they navigate their own journey through life."
    kazakh_text = translator.wrapper(english_text)
    print(kazakh_text)

# run()
