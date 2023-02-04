import content

class TelegramBotExample:
    def __init__(self) -> None:
        self.examples = content.EXAMPLES

    def get(self, index: int, lang: str) -> str:
        index = index % len(self.examples)
        return self.examples[index].get(lang, 'not-found')

    def increment(self, index: int):
        return (index + 1) % len(self.examples)
